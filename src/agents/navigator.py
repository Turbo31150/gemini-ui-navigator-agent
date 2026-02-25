"""Gemini UI Navigator Agent — real-time voice + vision interaction.

Manages a bidirectional session with Gemini Live API.
Sends audio + browser screenshots, receives audio + tool calls (click, type, etc.).

Pattern: Browser <-> WebSocket <-> FastAPI <-> Gemini Live API
                                      |
                                  Playwright (headless browser)
"""

import asyncio
import json
import logging
from google import genai
from google.genai import types

from src.config import PROJECT_ID, LOCATION, MODEL, DEFAULT_VOICE, SCREENSHOT_FPS
from src.tools.browser_tools import TOOL_DECLARATIONS, BrowserManager, execute_tool

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are Navigator, an intelligent UI automation agent powered by Gemini.
You can see the user's browser screen in real-time through screenshots and control it through actions.

Your capabilities:
- See and understand web page content visually from screenshots
- Click on elements by their visual position
- Type text into fields
- Scroll pages up and down
- Navigate to URLs
- Go back in browser history
- Press keyboard keys
- Read page text content

Behavior guidelines:
- When the user asks to navigate somewhere, use navigate_to with the full URL
- When clicking elements, describe what you're clicking before doing it
- Use the normalized 0-1000 coordinate grid based on the screenshot you see
- After each action, wait for the next screenshot to confirm the result
- If a click doesn't work, try slightly different coordinates
- Be concise in voice responses, describe what you see and what you're doing
- If the user asks what's on the page, use read_page_text or describe what you see
- Always confirm actions: "I'll click on the search bar now" then execute
- If you're unsure about coordinates, describe the element and ask for confirmation

Example interactions:
User: "Go to Wikipedia"
You: "Navigating to Wikipedia now." [call navigate_to with https://www.wikipedia.org]

User: "Search for artificial intelligence"
You: "I'll click on the search bar and type that in." [call click_element on search bar, then type_text]

User: "Scroll down"
You: "Scrolling down." [call scroll_page down]

User: "What does this page say?"
You: [call read_page_text, then summarize the content]
"""


class NavigatorSession:
    """Manages a single Gemini Live navigation session with browser control."""

    def __init__(self):
        self.client = genai.Client(
            vertexai=True,
            project=PROJECT_ID,
            location=LOCATION,
        )
        self.browser = BrowserManager()
        self.audio_input_queue: asyncio.Queue[bytes] = asyncio.Queue()
        self.event_queue: asyncio.Queue[dict | None] = asyncio.Queue()
        self._running = False
        self._screenshot_task = None

    def _build_config(self, voice: str = DEFAULT_VOICE) -> types.LiveConnectConfig:
        """Build the Gemini Live session configuration."""
        return types.LiveConnectConfig(
            response_modalities=[types.Modality.AUDIO],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name=voice,
                    )
                )
            ),
            system_instruction=types.Content(
                parts=[types.Part(text=SYSTEM_PROMPT)]
            ),
            tools=[types.Tool(function_declarations=TOOL_DECLARATIONS)],
            input_audio_transcription=types.AudioTranscriptionConfig(),
            output_audio_transcription=types.AudioTranscriptionConfig(),
        )

    async def _send_audio(self, session):
        """Continuously send audio chunks from queue to Gemini."""
        while self._running:
            try:
                chunk = await asyncio.wait_for(
                    self.audio_input_queue.get(), timeout=1.0
                )
                await session.send_realtime_input(
                    audio=types.Blob(
                        data=chunk,
                        mime_type="audio/pcm;rate=16000",
                    )
                )
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Send audio error: {e}")
                break

    async def _send_screenshots(self, session):
        """Continuously capture and send browser screenshots to Gemini."""
        while self._running:
            try:
                screenshot_bytes = await self.browser.screenshot()
                if screenshot_bytes:
                    await session.send_realtime_input(
                        media=types.Blob(
                            data=screenshot_bytes,
                            mime_type="image/jpeg",
                        )
                    )
                    # Also send screenshot to frontend for display
                    import base64
                    b64 = base64.b64encode(screenshot_bytes).decode()
                    await self.event_queue.put({
                        "type": "screenshot",
                        "data": b64,
                    })
                await asyncio.sleep(1.0 / SCREENSHOT_FPS)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Screenshot error: {e}")
                await asyncio.sleep(1.0)

    async def _receive_loop(self, session, audio_callback):
        """Receive responses from Gemini and dispatch events."""
        try:
            async for response in session.receive():
                if not self._running:
                    break

                server_content = response.server_content
                tool_call = response.tool_call

                if server_content:
                    # Audio output from model
                    if server_content.model_turn:
                        for part in server_content.model_turn.parts:
                            if part.inline_data:
                                await audio_callback(part.inline_data.data)

                    # Input transcription
                    if server_content.input_transcription:
                        text = server_content.input_transcription.text
                        if text and text.strip():
                            await self.event_queue.put({
                                "type": "input_transcription",
                                "text": text.strip(),
                            })

                    # Output transcription
                    if server_content.output_transcription:
                        text = server_content.output_transcription.text
                        if text and text.strip():
                            await self.event_queue.put({
                                "type": "output_transcription",
                                "text": text.strip(),
                            })

                    if server_content.turn_complete:
                        await self.event_queue.put({"type": "turn_complete"})

                    if server_content.interrupted:
                        await self.event_queue.put({"type": "interrupted"})

                # Tool/function calls from Gemini
                if tool_call:
                    for fc in tool_call.function_calls:
                        logger.info(f"Tool call: {fc.name}({fc.args})")
                        await self.event_queue.put({
                            "type": "tool_call",
                            "name": fc.name,
                            "args": dict(fc.args) if fc.args else {},
                        })

                        # Execute browser action
                        result = await execute_tool(
                            self.browser,
                            fc.name,
                            dict(fc.args) if fc.args else {},
                        )

                        await self.event_queue.put({
                            "type": "tool_result",
                            "name": fc.name,
                            "result": json.loads(result),
                        })

                        # Send result back to Gemini
                        await session.send_tool_response(
                            function_responses=[
                                types.FunctionResponse(
                                    name=fc.name,
                                    response={"result": result},
                                )
                            ]
                        )

        except Exception as e:
            logger.error(f"Receive loop error: {e}")
        finally:
            await self.event_queue.put(None)

    async def start(self, audio_callback):
        """Start the live navigation session.

        Args:
            audio_callback: async callable that receives PCM audio bytes
        """
        self._running = True
        config = self._build_config()

        # Start headless browser
        await self.browser.start()
        logger.info("Headless browser started")

        # Take initial screenshot and send as event
        import base64
        initial_ss = await self.browser.screenshot()
        if initial_ss:
            await self.event_queue.put({
                "type": "screenshot",
                "data": base64.b64encode(initial_ss).decode(),
            })

        logger.info(f"Connecting to Gemini Live: model={MODEL}")

        async with self.client.aio.live.connect(model=MODEL, config=config) as session:
            send_task = asyncio.create_task(self._send_audio(session))
            recv_task = asyncio.create_task(
                self._receive_loop(session, audio_callback)
            )
            screenshot_task = asyncio.create_task(
                self._send_screenshots(session)
            )

            try:
                while self._running:
                    try:
                        event = await asyncio.wait_for(
                            self.event_queue.get(), timeout=5.0
                        )
                    except asyncio.TimeoutError:
                        continue
                    if event is None:
                        break
                    yield event
            except asyncio.CancelledError:
                pass
            finally:
                self._running = False
                send_task.cancel()
                recv_task.cancel()
                screenshot_task.cancel()
                for task in [send_task, recv_task, screenshot_task]:
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
                await self.browser.stop()
                logger.info("Browser stopped")

    def stop(self):
        """Stop the session."""
        self._running = False

    async def feed_audio(self, data: bytes):
        """Feed audio data from client microphone."""
        await self.audio_input_queue.put(data)
