#!/bin/bash
# Automated Cloud Run deployment for Gemini UI Navigator Agent
# Usage: ./deploy/deploy.sh [PROJECT_ID] [REGION]

set -euo pipefail

PROJECT_ID="${1:-$(gcloud config get-value project)}"
REGION="${2:-us-central1}"
SERVICE_NAME="gemini-ui-navigator-agent"
IMAGE="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "=== Gemini UI Navigator Agent — Cloud Run Deployment ==="
echo "Project:  ${PROJECT_ID}"
echo "Region:   ${REGION}"
echo "Service:  ${SERVICE_NAME}"
echo ""

echo "[1/5] Enabling Google Cloud APIs..."
gcloud services enable \
    run.googleapis.com \
    aiplatform.googleapis.com \
    containerregistry.googleapis.com \
    cloudbuild.googleapis.com \
    --project="${PROJECT_ID}" --quiet

echo "[2/5] Building container image (includes Playwright + Chromium)..."
gcloud builds submit \
    --tag "${IMAGE}" \
    --project="${PROJECT_ID}" \
    --timeout=900 \
    --quiet

echo "[3/5] Deploying to Cloud Run..."
gcloud run deploy "${SERVICE_NAME}" \
    --image "${IMAGE}" \
    --region "${REGION}" \
    --project="${PROJECT_ID}" \
    --platform managed \
    --allow-unauthenticated \
    --set-env-vars "PROJECT_ID=${PROJECT_ID},LOCATION=${REGION},MODEL=gemini-live-2.5-flash-native-audio" \
    --memory 1Gi \
    --cpu 2 \
    --timeout 600 \
    --max-instances 5 \
    --min-instances 0 \
    --session-affinity \
    --quiet

echo "[4/5] Retrieving service URL..."
SERVICE_URL=$(gcloud run services describe "${SERVICE_NAME}" \
    --region="${REGION}" \
    --project="${PROJECT_ID}" \
    --format="value(status.url)")

echo ""
echo "[5/5] Deployment complete!"
echo "=========================================="
echo "Service URL: ${SERVICE_URL}"
echo "Health:      ${SERVICE_URL}/api/health"
echo "=========================================="
