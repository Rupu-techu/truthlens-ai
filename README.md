# 📰 TruthLens AI

**AI-Powered Fake News Detection System**

TruthLens AI is a machine learning-powered web application that helps users identify whether a news article is likely to be **Real** or **Fake**. The system combines Natural Language Processing (NLP), Machine Learning, and a modern web interface to provide fast and reliable predictions.

---

## 🚀 Features

* Detects fake and real news articles using Machine Learning
* Text preprocessing and cleaning pipeline
* TF-IDF based feature extraction
* Logistic Regression classifier
* FastAPI backend for model serving
* Interactive React frontend
* Confidence score for predictions
* REST API integration
* Responsive and modern user interface

---

## 🏗️ Project Architecture

```text
User Input
     │
     ▼
React Frontend
     │
     ▼
FastAPI Backend
     │
     ▼
TF-IDF Vectorizer
     │
     ▼
Logistic Regression Model
     │
     ▼
Prediction + Confidence Score
```

---

## 📂 Project Structure

```text
truthlens_ai/
│
├── apps/
│   ├── api/
│   │   ├── app/
│   │   ├── requirements.txt
│   │   └── main.py
│   │
│   └── web/
│       ├── src/
│       ├── public/
│       └── package.json
│
├── data/
│   ├── raw/
│   └── processed/
│
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   └── 02_preprocessing.ipynb
│
├── models/
│   ├── logistic_regression_model.pkl
│   └── tfidf_vectorizer.pkl
│
└── README.md
```

---

## 🧠 Machine Learning Pipeline

### Data Collection

Datasets were collected from publicly available fake news datasets and merged into a unified training dataset.

### Data Preprocessing

* Removed duplicates
* Removed missing values
* Text normalization
* Lowercasing
* URL removal
* Special character removal
* Whitespace cleaning

### Feature Engineering

TF-IDF (Term Frequency-Inverse Document Frequency) was used to transform text into numerical vectors suitable for machine learning.

### Model Training

Algorithm used:

* Logistic Regression

Evaluation Metrics:

* Accuracy: **99.07%**
* Precision: **99%**
* Recall: **99%**
* F1 Score: **99%**

---

## 🛠️ Tech Stack

### Frontend

* React
* TypeScript
* Tailwind CSS
* Vite

### Backend

* FastAPI
* Pydantic
* Uvicorn

### Machine Learning

* Scikit-Learn
* Pandas
* NumPy
* Joblib

---

## ⚙️ Installation

### Clone Repository

```bash
git clone <repository-url>
cd truthlens_ai
```

### Backend Setup

```bash
cd apps/api

pip install -r requirements.txt

uvicorn app.main:app --reload
```

Backend will run on:

```text
http://127.0.0.1:8000
```

API Documentation:

```text
http://127.0.0.1:8000/docs
```

---

### Frontend Setup

```bash
cd apps/web

npm install

npm run dev
```

Frontend will run on:

```text
http://localhost:5173
```

---

## 🔌 API Endpoint

### Predict News

**POST**

```http
/api/v1/predict
```

Request:

```json
{
  "text": "News article content goes here..."
}
```

Response:

```json
{
  "prediction": "Fake",
  "confidence": 90.59
}
```

---

## 📊 Model Performance

| Metric    | Score  |
| --------- | ------ |
| Accuracy  | 99.07% |
| Precision | 99%    |
| Recall    | 99%    |
| F1 Score  | 99%    |

---

## 🎯 Future Improvements

* Transformer-based models (BERT/RoBERTa)
* Real-time news URL analysis
* Explainable AI predictions
* News source credibility scoring
* User authentication
* Prediction history dashboard
* Cloud deployment

---

## 👨‍💻 Author

Developed as an AI & Machine Learning Internship Project.

**Project:** TruthLens AI
**Domain:** Fake News Detection using NLP and Machine Learning

---

## 📄 License

This project is licensed under the MIT License.
