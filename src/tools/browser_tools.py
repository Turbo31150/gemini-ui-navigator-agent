"""Browser automation tools for Gemini function calling.

Playwright controls a headless browser. Gemini sees screenshots and
decides which actions to take based on visual understanding.
"""

import asyncio
import base64
import json
import logging
from google.genai import types
from playwright.async_api import async_playwright, Browser, Page

from src.config import BROWSER_WIDTH, BROWSER_HEIGHT, SCREENSHOT_QUALITY, DEFAULT_URL

logger = logging.getLogger(__name__)

# ── Tool Declarations (sent to Gemini in LiveConnectConfig) ──────────────

TOOL_DECLARATIONS = [
    types.FunctionDeclaration(
        name="click_element",
        description="Click at a specific position on the page. Use normalized coordinates (0-1000) based on the screenshot dimensions.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "x": types.Schema(
                    type=types.Type.INTEGER,
                    description="X coordinate (0-1000 normalized grid)",
                ),
                "y": types.Schema(
                    type=types.Type.INTEGER,
                    description="Y coordinate (0-1000 normalized grid)",
                ),
                "description": types.Schema(
                    type=types.Type.STRING,
                    description="Brief description of what is being clicked",
                ),
            },
            required=["x", "y"],
        ),
    ),
    types.FunctionDeclaration(
        name="type_text",
        description="Type text into the currently focused element or at a specific position",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "text": types.Schema(
                    type=types.Type.STRING,
                    description="Text to type",
                ),
                "x": types.Schema(
                    type=types.Type.INTEGER,
                    description="X coordinate to click before typing (0-1000), optional",
                ),
                "y": types.Schema(
                    type=types.Type.INTEGER,
                    description="Y coordinate to click before typing (0-1000), optional",
                ),
                "clear_first": types.Schema(
                    type=types.Type.BOOLEAN,
                    description="Clear the field before typing, default false",
                ),
                "press_enter": types.Schema(
                    type=types.Type.BOOLEAN,
                    description="Press Enter after typing, default false",
                ),
            },
            required=["text"],
        ),
    ),
    types.FunctionDeclaration(
        name="scroll_page",
        description="Scroll the page up or down",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "direction": types.Schema(
                    type=types.Type.STRING,
                    description="Scroll direction: up or down",
                    enum=["up", "down"],
                ),
                "amount": types.Schema(
                    type=types.Type.INTEGER,
                    description="Scroll amount in pixels, default 400",
                ),
            },
            required=["direction"],
        ),
    ),
    types.FunctionDeclaration(
        name="navigate_to",
        description="Navigate the browser to a specific URL",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "url": types.Schema(
                    type=types.Type.STRING,
                    description="Full URL to navigate to (include https://)",
                ),
            },
            required=["url"],
        ),
    ),
    types.FunctionDeclaration(
        name="go_back",
        description="Go back to the previous page in browser history",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={},
        ),
    ),
    types.FunctionDeclaration(
        name="press_key",
        description="Press a keyboard key or key combination",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "key": types.Schema(
                    type=types.Type.STRING,
                    description="Key to press, e.g. Enter, Tab, Escape, Control+A, Control+C",
                ),
            },
            required=["key"],
        ),
    ),
    types.FunctionDeclaration(
        name="read_page_text",
        description="Extract and read the visible text content of the current page",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={},
        ),
    ),
    types.FunctionDeclaration(
        name="get_page_info",
        description="Get current page URL and title",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={},
        ),
    ),
]


# ── Browser Manager ────────────────────────────────────────────────────

class BrowserManager:
    """Manages a headless Playwright browser instance."""

    def __init__(self):
        self._playwright = None
        self._browser: Browser | None = None
        self._page: Page | None = None

    async def start(self) -> None:
        """Launch headless browser."""
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        context = await self._browser.new_context(
            viewport={"width": BROWSER_WIDTH, "height": BROWSER_HEIGHT},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131.0.0.0 Safari/537.36",
        )
        self._page = await context.new_page()
        await self._page.goto(DEFAULT_URL, wait_until="domcontentloaded")
        logger.info(f"Browser started: {BROWSER_WIDTH}x{BROWSER_HEIGHT}")

    async def stop(self) -> None:
        """Close browser."""
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
        self._browser = None
        self._page = None
        self._playwright = None

    async def screenshot(self) -> bytes:
        """Take a JPEG screenshot of the current page."""
        if not self._page:
            return b""
        return await self._page.screenshot(
            type="jpeg",
            quality=SCREENSHOT_QUALITY,
            full_page=False,
        )

    def _scale_x(self, x: int) -> int:
        """Convert from 0-1000 grid to actual pixels."""
        return int(x * BROWSER_WIDTH / 1000)

    def _scale_y(self, y: int) -> int:
        """Convert from 0-1000 grid to actual pixels."""
        return int(y * BROWSER_HEIGHT / 1000)

    async def click(self, x: int, y: int) -> dict:
        """Click at normalized coordinates."""
        px, py = self._scale_x(x), self._scale_y(y)
        await self._page.mouse.click(px, py)
        await asyncio.sleep(0.5)
        return {"action": "click", "x": px, "y": py, "status": "done"}

    async def type_text(self, text: str, x: int = None, y: int = None,
                        clear_first: bool = False, press_enter: bool = False) -> dict:
        """Type text, optionally clicking a position first."""
        if x is not None and y is not None:
            px, py = self._scale_x(x), self._scale_y(y)
            await self._page.mouse.click(px, py)
            await asyncio.sleep(0.3)

        if clear_first:
            await self._page.keyboard.press("Control+a")
            await asyncio.sleep(0.1)

        await self._page.keyboard.type(text, delay=30)

        if press_enter:
            await asyncio.sleep(0.1)
            await self._page.keyboard.press("Enter")

        await asyncio.sleep(0.5)
        return {"action": "type", "text": text, "status": "done"}

    async def scroll(self, direction: str, amount: int = 400) -> dict:
        """Scroll the page."""
        delta = -amount if direction == "up" else amount
        await self._page.mouse.wheel(0, delta)
        await asyncio.sleep(0.5)
        return {"action": "scroll", "direction": direction, "amount": amount, "status": "done"}

    async def navigate(self, url: str) -> dict:
        """Navigate to a URL."""
        try:
            await self._page.goto(url, wait_until="domcontentloaded", timeout=15000)
            return {"action": "navigate", "url": url, "title": await self._page.title(), "status": "done"}
        except Exception as e:
            return {"action": "navigate", "url": url, "error": str(e)}

    async def go_back(self) -> dict:
        """Go back in history."""
        await self._page.go_back(wait_until="domcontentloaded", timeout=10000)
        return {"action": "go_back", "url": self._page.url, "status": "done"}

    async def press_key(self, key: str) -> dict:
        """Press a key combination."""
        await self._page.keyboard.press(key)
        await asyncio.sleep(0.3)
        return {"action": "press_key", "key": key, "status": "done"}

    async def read_text(self) -> dict:
        """Extract visible text from page."""
        text = await self._page.inner_text("body")
        # Truncate for Gemini context
        truncated = text[:3000] if len(text) > 3000 else text
        return {"action": "read_text", "text": truncated, "url": self._page.url}

    async def get_info(self) -> dict:
        """Get page URL and title."""
        return {
            "url": self._page.url,
            "title": await self._page.title(),
        }


# ── Tool Dispatcher ─────────────────────────────────────────────────────

async def execute_tool(browser: BrowserManager, name: str, args: dict) -> str:
    """Execute a browser tool and return JSON result."""
    try:
        if name == "click_element":
            result = await browser.click(args["x"], args["y"])
        elif name == "type_text":
            result = await browser.type_text(
                args["text"],
                x=args.get("x"),
                y=args.get("y"),
                clear_first=args.get("clear_first", False),
                press_enter=args.get("press_enter", False),
            )
        elif name == "scroll_page":
            result = await browser.scroll(args["direction"], args.get("amount", 400))
        elif name == "navigate_to":
            result = await browser.navigate(args["url"])
        elif name == "go_back":
            result = await browser.go_back()
        elif name == "press_key":
            result = await browser.press_key(args["key"])
        elif name == "read_page_text":
            result = await browser.read_text()
        elif name == "get_page_info":
            result = await browser.get_info()
        else:
            result = {"error": f"Unknown tool: {name}"}
    except Exception as e:
        result = {"error": str(e)}

    return json.dumps(result, default=str)
