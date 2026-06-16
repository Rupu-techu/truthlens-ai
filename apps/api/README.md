# TruthLens AI API

The FastAPI backend loads these trained artifacts on startup:

- `app/ml/models/tfidf_vectorizer.pkl`
- `app/ml/models/logistic_regression_model.pkl`

If either file is missing, the application will fail fast during startup with a clear error message.

## Prediction endpoint

`POST /api/v1/predict`

### Request

```json
{
  "text": "news article text"
}
```

### Response

```json
{
  "prediction": "Fake",
  "confidence": 92.45
}
```

### Sample `curl`

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/predict" \
  -H "Content-Type: application/json" \
  -d "{\"text\":\"Breaking news article text goes here\"}"
```
