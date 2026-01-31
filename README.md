# ISEWS: Identity Stress Early-Warning System
# Official Submission for UIDAI Data Hackathon 2026
 Live Dashboard: [https://uidai-dashboard.streamlit.app/]

# Executive Summary
The Identity Stress Early-Warning System (ISEWS) is a predictive governance framework designed for the Aadhaar ecosystem. By reframing routine identity updates as "signals" of system pressure, ISEWS allows the Unique Identification Authority of India (UIDAI) to move from reactive troubleshooting to proactive infrastructure management.

# Modular Architecture: The 6-Layer Pipeline
This project follows a modular, layered architecture to transform raw Aadhaar logs into actionable governance insights.

Phase 1: Research & Signal Extraction

01_layer3_data_preparation.ipynb: Ingestion and cleaning of anonymized OGD datasets to ensure data integrity.

02_layer4_signal_extraction.ipynb: Temporal analysis to extract biometric and demographic update trends across 2025.

03_layer5_indicators_ml.ipynb: Engineering the "Update-to-Enrolment" Ratio and training an Isolation Forest model to detect anomalies.

04_layer6_visualisation_storytelling.ipynb: Final validation of results and cross-referencing rule-based stress indicators with ML scores.

Phase 2: Live Command Centre Deployment

app.py: A high-performance Streamlit dashboard designed for decision-makers.

Geospatial Analysis: Interactive Plotly heatmaps identifying regional "Stress Belts".

Precision Targeting: Identifying high-stress districts like Beawar and Thane for operational triage.

# Repository Breakdown

Core Application

app.py: Main Streamlit application file.

requirements.txt: List of Python dependencies (Pandas, Scikit-learn, Plotly, Streamlit).

Research & Data Science

Layered Notebooks (01-04): Modular Jupyter Source Files documenting the end-to-end ML journey.

final_uidai_data.csv: Unified master dataset powering the dashboard (synced with identity_metrics.csv).

biometric_monthly.csv / demographic_monthly.csv: Processed time-series transaction logs.

Project Documentation

ISEWS_UIDAI_Hackathon_Submission.pdf: Comprehensive technical report and project abstract.

UIDAI_Hackathon_ISEWS_Spotlight.pdf: Visual presentation slides and carousel spotlight.

# Installation & Local Usage

To replicate this environment locally:

Clone the repository: git clone [https://github.com/anuskaGHS/ISEWS------Identity-Stress-Early-Warning-System-]

Install dependencies: pip install -r requirements.txt

Run the dashboard: streamlit run app.py

# Meet the Team:
Anuska Ghosh (Team Lead) 

Likitha S 

# Note: This project was developed as part of the UIDAI Data Hackathon 2026.
