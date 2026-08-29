#!/bin/bash
set -e

echo "Starting backend (FastAPI)..."
gunicorn -b 0.0.0.0:8080 -k uvicorn.workers.UvicornWorker backend.app:app &

echo "Starting Streamlit..."
exec streamlit run frontend/appst.py \
  --server.port=${PORT} \
  --server.address=0.0.0.0
