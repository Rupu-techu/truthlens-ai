# Streamlit Deployment Guide

This repository now includes a minimal Streamlit entry point for deployment only.
It does not replace the React frontend, and it does not change the FastAPI routes or ML logic.

## What was added

- `streamlit_app.py` as the Streamlit entry point
- root `requirements.txt` for Streamlit Community Cloud
- `runtime.txt` pinned to Python 3.12
- `.streamlit/config.toml` for basic runtime behavior

## How it works

The Streamlit app:

- imports the existing FastAPI application from `apps/api/app/main.py`
- loads the trained TF-IDF vectorizer and logistic regression model from `data/models`
- runs a startup smoke test against the existing `PredictionService`
- validates that the FastAPI health route exists
- logs deployment status and model loading details

No new fake-news interface is introduced.
No forms, text areas, or buttons are added.

## Repository layout expected by Streamlit Cloud

Streamlit Community Cloud runs from the repository root and expects the app entry point and dependency file to be available from there.

Required files:

- `streamlit_app.py`
- `requirements.txt`
- `data/models/tfidf_vectorizer.pkl`
- `data/models/logistic_regression_model.pkl`

Optional files:

- `.streamlit/config.toml`
- `runtime.txt`

## Local startup

From the repository root:

```bash
streamlit run streamlit_app.py
```

## Streamlit Community Cloud deployment

1. Push this repository to GitHub.
2. Open Streamlit Community Cloud and create a new app.
3. Select the repository.
4. Set the app file to `streamlit_app.py`.
5. Deploy.

## GitHub repository deployment checklist

1. Confirm `data/models/tfidf_vectorizer.pkl` is committed.
2. Confirm `data/models/logistic_regression_model.pkl` is committed.
3. Confirm root `requirements.txt` includes `streamlit` and `scikit-learn==1.6.1`.
4. Confirm the app file is `streamlit_app.py` at the repository root.
5. Commit and push the changes.
6. Re-deploy from Streamlit Community Cloud.

## Validation steps

After deployment, the app should show:

- project root detection
- model directory detection
- successful artifact loading
- FastAPI health route availability
- a smoke-test prediction result

If startup validation fails, check the Streamlit logs for the exact missing file or import error.
