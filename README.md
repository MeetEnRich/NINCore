# NINCore: Identity Governance and Risk Engine

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Framework-009688)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B)
![Scikit-Learn](https://img.shields.io/badge/Machine%20Learning-Scikit--Learn-F7931E)

**NINCore** is a machine learning-powered Identity Governance and Risk Engine designed to provide real-time behavioral monitoring and probabilistic risk assessment for Nigeria's National Identification Number (NIN) ecosystem. 

This system bridges the gap between fragmented identity databases (Banking, Health, Education, Transport, and Telecommunications) by acting as an interoperable, NIN-centric linkage layer. It uses a Random Forest Classifier to assign dynamic "Identity Confidence Scores" and detect multi-vector fraud patterns such as *Impossible Travel*, *Credential Stuffing*, and *Identity Conflicts*.

---

##  Architecture

NINCore consists of three main decoupled layers:
1. **Machine Learning Risk Engine (`models/`)**: A pre-trained Random Forest model that evaluates 20 distinct demographic, sectoral, and behavioral features to detect anomalies.
2. **REST API (`api/`)**: A FastAPI-based service that securely exposes endpoints for real-time identity verification, risk scoring, and audit logging.
3. **Governance Dashboard (`dashboard/`)**: A Streamlit application that allows administrators to visualize national identity risk trends, monitor real-time API logs, and investigate flagged high-risk profiles.

---

##  Project Structure

```text
NINCore/
├── api/                  # FastAPI application and routes
├── config/               # Configuration and environment variables
├── dashboard/            # Streamlit governance frontend
├── data/                 # Raw and processed synthetic data
├── database/             # SQLite database and schemas
├── docs/                 # Documentation and research reports
├── logs/                 # System audit and API logs
├── models/               # ML models and inference logic
│   └── saved/            # Serialized models (.pkl)
├── notebooks/            # Jupyter notebooks for exploratory data analysis (EDA) and model training
├── scripts/              # Utility scripts (Dataset generation, DB setup)
├── tests/                # Unit and integration tests
├── .env.example          # Example environment variables
├── run_api.py            # Entry point for the FastAPI server
├── run_dashboard.py      # Entry point for the Streamlit dashboard
└── requirements.txt      # Project dependencies
```

---

##  Getting Started

### 1. Prerequisites
- Python 3.10+
- Git

### 2. Installation
Clone the repository and install the required dependencies:

```bash
git clone https://github.com/MeetEnRich/NINCore.git
cd NINCore

# Create and activate a virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Database Setup & Data Generation
Initialize the SQLite database schema and generate the synthetic demographic dataset.

```bash
# Setup the SQLite Database
python scripts/setup_database.py

# Generate 50,000 synthetic NIN records
python scripts/generate_dataset.py
```

### 4. Running the System

You will need two separate terminal windows/tabs to run the API and Dashboard simultaneously.

**Terminal 1: Start the FastAPI Backend**
```bash
python run_api.py
# The API will be available at: http://localhost:8000
# API Documentation (Swagger UI): http://localhost:8000/docs
```

**Terminal 2: Start the Streamlit Dashboard**
```bash
python run_dashboard.py
# The dashboard will open automatically in your browser at: http://localhost:8501
```

---

##  Machine Learning Model
The system uses a Random Forest algorithm trained on a highly engineered synthetic dataset to mimic Nigerian sectoral behaviors. It tackles severe class imbalances using SMOTE (Synthetic Minority Oversampling Technique) and outputs a probabilistic risk score (0 to 1). 
- Scores `> 0.7` are flagged as **High Risk**.
- Scores `<= 0.7` are cleared as **Low Risk**.

---

##  Security & Privacy
NINCore is designed with a Privacy-by-Design approach. It implements an interoperable linkage layer that connects disparate sector records without physically merging the sensitive databases, adhering to the principles of the Nigeria Data Protection Act (NDPA 2023).

---

##  Author
**Stefan Habila Musa**  
*(2021/CP/CSC/0296)*  
Federal University of Lafia  
Department of Computer Science 
