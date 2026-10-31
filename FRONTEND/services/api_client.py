
import joblib
import pandas as pd
import spacy

from pathlib import Path
from functools import lru_cache
from sklearn.metrics.pairwise import cosine_similarity
ANALYSIS_STAGES = [
    "Loading incident report",
    "Predicting root cause",
    "Predicting risk level",
    "Extracting incident information",
    "Finding similar incidents",
    "Preparing analysis report"
]

# ============================================================
# CUSTOM API ERROR
# ============================================================

class ApiError(Exception):
    """Custom exception used by the Streamlit frontend."""
    pass


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODEL_DIR = PROJECT_ROOT / "MODELS"
DATA_DIR = PROJECT_ROOT / "DATA" / "processed"

DATA_PATH = DATA_DIR / "safety_incidents_cleaned.csv"

ROOT_CAUSE_PATH = MODEL_DIR / "safety_root_cause_model.joblib"
RISK_MODEL_PATH = MODEL_DIR / "risk_level_model.joblib"
EXTRACTION_PATH = MODEL_DIR / "incident_extraction_engine.joblib"
SIMILARITY_PATH = MODEL_DIR / "similar_incident_engine.joblib"

USE_MOCK = False


# ============================================================
# LOAD MODELS AND DATA
# ============================================================

@lru_cache(maxsize=1)
def load_resources():

    required_files = [
        ROOT_CAUSE_PATH,
        RISK_MODEL_PATH,
        EXTRACTION_PATH,
        SIMILARITY_PATH,
        DATA_PATH
    ]

    for file in required_files:
        if not file.exists():
            raise FileNotFoundError(
                f"Required project file not found: {file}"
            )

    resources = {
        "root_cause_model": joblib.load(ROOT_CAUSE_PATH),
        "risk_model": joblib.load(RISK_MODEL_PATH),
        "extraction_engine": joblib.load(EXTRACTION_PATH),
        "similarity_engine": joblib.load(SIMILARITY_PATH),
        "history": pd.read_csv(DATA_PATH)
    }

    return resources


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def clean_value(value, default="Not specified"):

    if value is None:
        return default

    if pd.isna(value):
        return default

    value = str(value).strip()

    if value.lower() in ("", "nan", "none"):
        return default

    return value


def find_column(df, possible_names):

    column_lookup = {
        str(column).lower(): column
        for column in df.columns
    }

    for name in possible_names:
        if name.lower() in column_lookup:
            return column_lookup[name.lower()]

    return None


def get_row_value(row, possible_names, default="Not specified"):

    for name in possible_names:
        if name in row.index:
            return clean_value(row[name], default)

    return default


def notify_stage(callback, message):

    if callback is not None:
        callback(message)


# ============================================================
# ROOT CAUSE PREDICTION
# ============================================================

import numpy as np

def predict_root_cause(text):
    model = load_resources()["root_cause_model"]

    scores = model.decision_function([str(text)])
    classes = model.classes_

    exp_scores = np.exp(scores[0] - np.max(scores[0]))
    confidence_scores = exp_scores / np.sum(exp_scores)

    best_index = np.argmax(scores[0])

    prediction = str(classes[best_index])
    confidence = round(float(confidence_scores[best_index]), 4)

    return prediction, confidence

# ============================================================
# RISK LEVEL PREDICTION
# ============================================================

def predict_risk_level(text, incident_data=None):

    model = load_resources()["risk_model"]

    incident_data = incident_data or {}

    feature_names = list(model.feature_names_in_)

    defaults = {
        "clean_description": str(text).lower(),
        "incident_type": "Not specified",
        "department": "Not specified",
        "location": "Not specified",
        "shift": "Not specified",
        "employee_role": "Not specified",
        "experience_level": "Not specified",
        "equipment_type": "Not Applicable",
        "equipment_status": "Not Applicable"
    }

    row = {}

    for feature in feature_names:

        value = incident_data.get(
            feature,
            defaults.get(feature, "Not specified")
        )

        row[feature] = clean_value(value)

    input_df = pd.DataFrame(
        [row],
        columns=feature_names
    )

    prediction = model.predict(input_df)[0]

    return str(prediction)


# ============================================================
# INFORMATION EXTRACTION
# ============================================================

@lru_cache(maxsize=1)
def load_spacy_model():

    try:
        return spacy.load("en_core_web_sm")
    except (OSError, ImportError):
        return None


def extract_incident_information(text):

    engine = load_resources()["extraction_engine"]

    text_lower = str(text).lower()

    keyword_groups = {
        "hazards": "hazard_keywords",
        "equipment": "equipment_keywords",
        "locations": "location_keywords",
        "safety_factors": "safety_factor_keywords"
    }

    extracted = {}

    for output_name, engine_key in keyword_groups.items():

        keywords = engine.get(engine_key, [])

        matches = [
            keyword
            for keyword in keywords
            if keyword.lower() in text_lower
        ]

        extracted[output_name] = sorted(set(matches))

    # Named entity extraction using spaCy.
    named_entities = []

    nlp = load_spacy_model()

    if nlp is not None:
        try:
            doc = nlp(str(text))

            named_entities = [
                entity.text
                for entity in doc.ents
                if entity.label_ in (
                    "ORG", "PERSON", "GPE", "PRODUCT"
                )
            ]

        except Exception:
            named_entities = []

    extracted["named_entities"] = named_entities

    return extracted


# ============================================================
# SIMILAR HISTORICAL INCIDENTS
# ============================================================

def get_similar_incidents(text, top_n=5):

    engine = load_resources()["similarity_engine"]

    vectorizer = engine["vectorizer"]
    tfidf_matrix = engine["tfidf_matrix"]
    history = engine["history"]

    query = vectorizer.transform([str(text)])

    scores = cosine_similarity(
        query,
        tfidf_matrix
    ).flatten()

    # Get the highest similarity scores.
    indices = scores.argsort()[::-1]

    # Ignore zero-similarity results.
    indices = [
        index
        for index in indices
        if scores[index] > 0
    ][:top_n]

    if len(indices) == 0:
        return pd.DataFrame()

    results = history.iloc[indices].copy()

    results["similarity_score"] = (
        scores[indices] * 100
    ).round(2)

    return results.reset_index(drop=True)


# ============================================================
# SAFETY RECOMMENDATIONS
# ============================================================

def get_recommendations(risk_level):

    recommendations = {

        "High": [
            "Stop the affected operation if an immediate danger exists.",
            "Inform the site safety officer immediately.",
            "Inspect the affected equipment and surrounding area.",
            "Implement corrective measures before restarting work.",
            "Review the relevant safety procedures."
        ],

        "Medium": [
            "Schedule corrective maintenance or housekeeping.",
            "Review existing preventive safety controls.",
            "Monitor the area for recurring hazards."
        ],

        "Low": [
            "Maintain routine safety inspections.",
            "Reinforce employee safety awareness.",
            "Continue monitoring existing controls."
        ]
    }

    return recommendations.get(
        str(risk_level).strip().title(),
        ["Conduct a safety inspection and review the incident."]
    )


# ============================================================
# MAIN INCIDENT ANALYSIS
# ============================================================



def analyze_incident(text, incident_data=None, on_stage=None):

    text = str(text).strip()

    if not text:
        raise ApiError("Please enter an incident description.")

    incident_data = incident_data or {}

    try:
        # 1. Root cause prediction
        notify_stage(on_stage, "Predicting root cause...")
        root_cause, root_cause_confidence = predict_root_cause(text)

        # 2. Risk level prediction
        notify_stage(on_stage, "Predicting risk level...")
        risk_level = predict_risk_level(text, incident_data)

        # 3. Information extraction
        notify_stage(on_stage, "Extracting incident information...")
        extracted = extract_incident_information(text)

        if not isinstance(extracted, dict):
            extracted = {}

        # Normalize extracted information for the frontend
        extracted = {
            "equipment": extracted.get("equipment", []),
            "materials": extracted.get(
                "materials",
                extracted.get("chemicals", [])
            ),
            "hazards": extracted.get("hazards", []),
            "locations": extracted.get("locations", []),
            "safety_factors": extracted.get("safety_factors", []),
            "named_entities": extracted.get("named_entities", []),

            "human": extracted.get("human", []),
            "maintenance": extracted.get("maintenance", []),
            "operational": extracted.get("operational", []),
            "environmental": extracted.get("environmental", [])
        }

        # 4. Similar historical incidents
        notify_stage(
            on_stage,
            "Finding similar historical incidents..."
        )

        similar = get_similar_incidents(text, top_n=5)

        if similar is not None and not similar.empty:
            similar_records = similar.to_dict(orient="records")
        else:
            similar_records = []

        # 5. Prepare incident details
        notify_stage(on_stage, "Preparing analysis report...")

        incident = {
            "id": incident_data.get("incident_id", "New incident"),
            "description": text,
            "summary": text[:300],
            "date": incident_data.get(
                "incident_date", "New incident"
            ),
            "type": incident_data.get(
                "incident_type", "Not specified"
            ),
            "department": incident_data.get(
                "department", "Not specified"
            ),
            "location": incident_data.get(
                "location",
                extracted["locations"][0]
                if extracted["locations"] else "Not specified"
            ),
            "equipment": incident_data.get(
                "equipment_type",
                extracted["equipment"][0]
                if extracted["equipment"] else "Not specified"
            )
        }

        # 6. Final result
        result = {
            "incident": incident,

            "extracted_information": extracted,

            "severity": {
                "label": risk_level,
                "score": None
            },

            "historical_analysis": {
                "similar_incidents": similar_records,
                "total_matches": len(similar_records)
            },

            "similar_incidents": similar_records,

          "root_causes": [
    {
        "cause": root_cause,
        "confidence": root_cause_confidence,
        "evidence": [],
        "supporting_factors": []
    }
],

            "recommendations": get_recommendations(risk_level),

            "report_text": text
        }

        notify_stage(on_stage, "Analysis completed!")

        return result

    except ApiError:
        raise

    except Exception as error:
        raise ApiError(
            f"Incident analysis failed: {error}"
        ) from error


# ============================================================
# HISTORICAL INCIDENT LIST
# ============================================================

def list_incidents():

    df = load_resources()["history"].copy()

    date_col = find_column(
        df,
        ["incident_date", "date"]
    )

    description_col = find_column(
        df,
        [
            "clean_description",
            "incident_description",
            "accident_details",
            "description"
        ]
    )

    cause_col = find_column(
        df,
        [
            "root_cause_category",
            "cause",
            "root_cause"
        ]
    )

    type_col = find_column(
        df,
        ["incident_type", "type"]
    )

    location_col = find_column(
        df,
        ["location", "plant_location"]
    )

    equipment_col = find_column(
        df,
        ["equipment_type", "equipment"]
    )

    severity_col = find_column(
        df,
        ["severity_level", "severity"]
    )

    risk_col = find_column(
        df,
        ["risk_score"]
    )

    # Date.
    if date_col:
        df["date"] = pd.to_datetime(
            df[date_col],
            errors="coerce"
        )
    else:
        df["date"] = pd.NaT

    # Incident ID.
    if "incident_id" in df.columns:
        df["id"] = df["incident_id"].astype(str)
    else:
        df["id"] = df.index.astype(str)

    # Description.
    if description_col:
        df["summary"] = (
            df[description_col]
            .fillna("")
            .astype(str)
        )
    else:
        df["summary"] = ""

    # Incident type.
    df["type"] = (
        df[type_col].fillna("Not specified")
        if type_col else "Not specified"
    )

    # Location.
    df["unit"] = (
        df[location_col].fillna("Not specified")
        if location_col else "Not specified"
    )

    # Equipment.
    df["equipment"] = (
        df[equipment_col].fillna("Not specified")
        if equipment_col else "Not specified"
    )

    # Recorded severity.
    df["severity"] = (
        df[severity_col].fillna("Not assessed")
        if severity_col else "Not assessed"
    )

    # Recorded risk score, if available.
    if risk_col:
        df["severity_score"] = pd.to_numeric(
            df[risk_col],
            errors="coerce"
        )
    else:
        df["severity_score"] = None

    # Root cause.
    df["root_cause"] = (
        df[cause_col].fillna("Not specified")
        if cause_col else "Not specified"
    )

    return df.dropna(
        subset=["date"]
    ).copy()


# ============================================================
# SINGLE HISTORICAL INCIDENT ANALYSIS
# ============================================================

def get_incident_analysis(incident_id):

    df = list_incidents()

    matched = df[
        df["id"].astype(str) == str(incident_id)
    ]

    if matched.empty:
        raise ApiError(
            f"Historical incident not found: {incident_id}"
        )

    row = matched.iloc[0]

    incident_data = {
        "incident_date": str(row["date"].date()),
        "incident_type": clean_value(row["type"]),
        "department": get_row_value(row, ["department"]),
        "location": clean_value(row["unit"]),
        "shift": get_row_value(row, ["shift"]),
        "employee_role": get_row_value(row, ["employee_role"]),
        "experience_level": get_row_value(row, ["experience_level"]),
        "equipment_type": clean_value(row["equipment"]),
        "equipment_status": get_row_value(row, ["equipment_status"])
    }

    result = analyze_incident(
        row["summary"],
        incident_data
    )

    # Display the historical severity recorded in the dataset.
    result["severity"] = {
        "label": clean_value(
            row["severity"],
            "Not assessed"
        ),
        "score": (
            float(row["severity_score"])
            if pd.notna(row["severity_score"])
            else None
        )
    }

    result["incident"]["id"] = str(row["id"])

    return result
