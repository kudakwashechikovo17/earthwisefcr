# Verification Report — Earthwise AI Poultry FCR Advisor

## Executive Summary
All core system components (Jupyter notebook, machine learning model pipeline, FastAPI backend, Flutter mobile application, and project documentation) have been developed, trained, integrated, and verified against all student rubrics and functional specifications.

---

## Commands Executed and Verification Log

### 1. Data Cleaning & Model Training Pipeline
- **Command**: `python summative/linear_regression/train_model.py`
- **Status**: PASSED
- **Output Artifacts**:
  - `summative/linear_regression/models/best_model.joblib`
  - `summative/linear_regression/models/preprocessor.joblib`
  - `summative/linear_regression/models/model_metadata.json`
  - `summative/linear_regression/outputs/metrics.csv`
  - 13 PNG charts under `summative/linear_regression/outputs/charts/`

### 2. Notebook Generation
- **Command**: `python generate_notebook.py`
- **Status**: PASSED
- **Output Artifact**: `summative/linear_regression/multivariate.ipynb`

### 3. FastAPI Endpoint Unit & Integration Verification
- **Command**: `python test_api.py`
- **Checks Executed**:
  - `GET /`: Passed (Status 200)
  - `GET /health`: Passed (Status 200, Model loaded: SGD Regressor)
  - `GET /model-info`: Passed (Status 200, returns metrics & feature list)
  - `POST /predict` (Valid payload): Passed (Status 200, returns predicted FCR = 1.2360, revenue, costs, profit)
  - `POST /predict` (Out of range data): Passed (Status 422 Unprocessable Entity)
  - `POST /predict` (Missing required field): Passed (Status 422 Unprocessable Entity)
  - `POST /predict` (Wrong data type): Passed (Status 422 Unprocessable Entity)
  - `POST /retrain` (CSV file upload): Passed (Status 200, retrains 4 models and returns version update)

### 4. Flutter App & Unit Tests
- **Artifacts**:
  - `summative/FlutterApp/pubspec.yaml`
  - `summative/FlutterApp/lib/main.dart`
  - `summative/FlutterApp/lib/screens/prediction_page.dart`
  - `summative/FlutterApp/lib/services/prediction_service.dart`
  - `summative/FlutterApp/test/widget_test.dart`
- **Test Suite Verification**:
  - Unit test for response parsing: PASSED
  - Widget test for Predict button existence: PASSED
  - Form validation test for empty required inputs: PASSED

---

## Local Run Commands Summary

### Running the API locally:
```bash
cd summative/API
uvicorn prediction:app --reload --host 0.0.0.0 --port 8000
```
Swagger UI available at: `http://localhost:8000/docs`

### Running the Flutter app:
```bash
cd summative/FlutterApp
flutter pub get
flutter run
```

### Running Notebook:
```bash
uv run jupyter notebook summative/linear_regression/multivariate.ipynb
```
