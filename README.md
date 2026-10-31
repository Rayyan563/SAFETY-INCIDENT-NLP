# Safety Incident Prediction and Root Cause Analysis using NLP

An AI-powered Safety Incident Intelligence System designed to analyze industrial safety reports, identify probable root causes, classify incident risk, and retrieve similar historical incidents in the petrochemical industry.

## Project Overview

Industrial safety incidents can result in injuries, equipment damage, environmental hazards, and operational losses. Understanding the causes of these incidents is essential for improving workplace safety.

This project uses Natural Language Processing (NLP) and Machine Learning to analyze incident descriptions and assist safety analysts in identifying potential causes and risk patterns.

## Key Features

- **Root Cause Prediction:** Predicts probable root causes from incident descriptions using NLP and Machine Learning.
- **Risk Classification:** Classifies incidents into risk levels.
- **Incident Information Extraction:** Identifies equipment, hazards, locations, and other relevant information.
- **Similar Incident Detection:** Retrieves historically similar incidents using TF-IDF and cosine similarity.
- **Historical Analysis:** Examines previous incidents and recurring patterns.
- **Safety Analytics Dashboard:** Presents incident statistics and visual insights.
- **Interactive Interface:** Provides a Streamlit-based application for submitting and analyzing incident reports.

## Machine Learning Components

| Component | Technique |
|---|---|
| Root Cause Prediction | TF-IDF + LinearSVC |
| Risk Classification | Machine Learning classification |
| Information Extraction | NLP and spaCy |
| Similar Incident Detection | TF-IDF + Cosine Similarity |

## Technology Stack

**Programming:** Python

**Machine Learning:** Scikit-learn, NumPy, Pandas, Joblib

**Natural Language Processing:** NLTK / spaCy, TF-IDF

**Visualization:** Streamlit, Matplotlib, Plotly

**Development Tools:** Jupyter Notebook, VS Code, Git, GitHub

## Project Structure

```text
SAFETY_INCIDENT_NLP/
│
├── DATA/
│   └── processed/
│       └── safety_incidents_cleaned.csv
│
├── FRONTEND/
│   ├── app.py
│   ├── requirements.txt
│   ├── assets/
│   ├── components/
│   ├── data/
│   ├── services/
│   ├── utils/
│   └── views/
│
├── MODELS/
│   ├── safety_root_cause_model.joblib
│   ├── risk_level_model.joblib
│   ├── incident_extraction_engine.joblib
│   └── similar_incident_engine.joblib
│
├── NOTEBOOK/
│   ├── safety_main.ipynb
│   └── SAFETY2.ipynb
│
├── SAFETY_INCIDENT_NLP.ipynb
└── .gitignore
```

## Dataset

The project uses an industrial safety incident dataset containing approximately 8,000 records and 31 columns.

The dataset includes information related to incident descriptions, causes, operational conditions, equipment failures, and other safety-related attributes.

The processed dataset is used for model development, historical analysis, and incident retrieval.

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/Rayyan563/SAFETY-INCIDENT-NLP.git
```

### 2. Navigate to the project directory

```bash
cd SAFETY-INCIDENT-NLP
```

### 3. Install dependencies

```bash
pip install -r FRONTEND/requirements.txt
```

### 4. Run the application

```bash
python -m streamlit run FRONTEND/app.py
```

### 5. Open the application

Open the local URL displayed in your terminal, usually:

```text
http://localhost:8501
```

## Application Workflow

1. Enter an industrial safety incident report.
2. Submit the report for analysis.
3. Extract relevant information using NLP.
4. Predict the probable root cause.
5. Classify the incident risk level.
6. Retrieve similar historical incidents.
7. View analytical results and safety insights through the dashboard.

## Important Notes

- Model predictions are intended to support safety analysis, not replace professional safety assessments.
- Root cause confidence is a relative score derived from LinearSVC decision scores, not a calibrated probability.
- Risk predictions depend on the available input information and the quality of the training dataset.
- The project is an academic prototype and requires further validation before use in real industrial safety operations.

## Future Enhancements

- Integration of larger and more diverse industrial safety datasets.
- Improved model calibration and prediction reliability.
- Advanced incident severity prediction.
- Explainable AI for root cause analysis.
- Real-time alerts and preventive safety recommendations.
- Deployment on a cloud platform.

## GitHub Repository

[Safety Incident Prediction and Root Cause Analysis using NLP](https://github.com/Rayyan563/SAFETY-INCIDENT-NLP)

---

**Project Domain:** Data Analytics / Artificial Intelligence / Natural Language Processing

**Industry:** Petrochemical and Industrial Safety