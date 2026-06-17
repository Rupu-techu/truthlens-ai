# TruthLens AI Streamlit Deployment Guide

TruthLens AI now includes a branded Streamlit launcher that keeps the existing React frontend as the primary experience while adding deployment diagnostics for Streamlit Community Cloud.

The launcher:

- preserves the React + Vite frontend in `apps/web`
- reuses the existing FastAPI backend in `apps/api/app`
- loads the trained TF-IDF vectorizer and Logistic Regression model from `data/models`
- validates the FastAPI startup path and health endpoint
- auto-detects the FastAPI health route (`/api/v1/health` or `/health`)
- reports frontend URL configuration and best-effort reachability
- shows model fingerprint and artifact metadata for quick deployment checks

## Files Added Or Updated

- `streamlit_app.py`
- `.streamlit/config.toml`
- `requirements.txt`
- `STREAMLIT_DEPLOYMENT.md`

## Runtime Expectations

Streamlit Community Cloud runs from the repository root, so these paths must remain intact:

- `apps/api/app`
- `data/models/tfidf_vectorizer.pkl`
- `data/models/logistic_regression_model.pkl`

The launcher resolves the project root dynamically, so it works whether you run it locally or deploy from GitHub.

## Environment Variables

The Streamlit launcher reads these optional values:

- `TRUTHLENS_FRONTEND_URL`
- `TRUTHLENS_MODEL_VERSION`

If `TRUTHLENS_FRONTEND_URL` is not set, the launcher falls back to `http://localhost:5173`.

If `TRUTHLENS_MODEL_VERSION` is not set, the launcher derives a version label from the model artifact fingerprints.

## Local Run

From the repository root:

```bash
streamlit run streamlit_app.py
```

The launcher will:

- import the FastAPI application
- load the model artifacts
- run a smoke-test prediction
- probe the health endpoint
- display the configured frontend URL

## Streamlit Community Cloud Setup

1. Push the repository to GitHub.
2. Open Streamlit Community Cloud.
3. Create a new app from the repository.
4. Set the app file to `streamlit_app.py`.
5. Make sure the repository root is used as the working directory.
6. Add `TRUTHLENS_FRONTEND_URL` if your React frontend is deployed separately.
7. Deploy the app.

## GitHub Deployment Steps

1. Commit `streamlit_app.py`.
2. Commit `.streamlit/config.toml`.
3. Commit the updated `requirements.txt`.
4. Commit this deployment guide.
5. Push the branch to GitHub.
6. Connect or reconnect Streamlit Community Cloud to the repository.
7. Deploy `streamlit_app.py` from the repository root.

## Validation Checklist

After deployment, confirm the launcher shows:

- project root detection
- `apps/api/app` import path resolution
- `data/models` artifact detection
- model loading success
- smoke-test prediction output
- FastAPI startup success
- the FastAPI health route returning `{"status": "ok"}`
- frontend URL configuration status
- model version or artifact fingerprint

## Troubleshooting

If deployment fails, check the Streamlit logs for these common issues:

- missing `pydantic-settings`
- missing `httpx`
- missing model artifacts in `data/models`
- invalid `TRUTHLENS_FRONTEND_URL`
- import errors inside `apps/api/app`

If the frontend URL is configured but unreachable, the launcher still starts. The frontend button remains available, and the error is shown as a deployment warning rather than a hard failure.

## What This Launcher Does Not Change

- It does not replace the React UI.
- It does not modify prediction logic.
- It does not retrain or rewrite the model files.
- It does not change the existing FastAPI routes.

## Recommended Deployment Order

1. Verify the FastAPI backend starts locally.
2. Verify the React frontend still runs locally.
3. Deploy the Streamlit launcher from the repository root.
4. Set `TRUTHLENS_FRONTEND_URL` to the deployed React URL.
5. Re-check the launcher status cards and backend health check.

## Final Deployment Checklist

- `streamlit_app.py` exists at the repository root.
- `.streamlit/config.toml` is committed.
- `requirements.txt` includes `streamlit`, `pydantic-settings`, and `httpx`.
- `apps/api/app` remains unchanged.
- `data/models` contains the trained artifacts.
- `TRUTHLENS_FRONTEND_URL` is configured in Streamlit Cloud when needed.
- The launcher shows the React frontend button, backend health status, and model status.
