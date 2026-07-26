# Earthwise AI Poultry Production and Feed Efficiency Advisor

### 📌 Submission Overview & Key Links
- 🔗 **GitHub Repository**: [https://github.com/kudakwashechikovo17/earthwisefcr](https://github.com/kudakwashechikovo17/earthwisefcr)
  - 📊 **Dataset File**: [poultry_data.csv](https://github.com/kudakwashechikovo17/earthwisefcr/blob/main/summative/linear_regression/data/poultry_data.csv)
  - 📓 **Jupyter Notebook**: [multivariate.ipynb](https://github.com/kudakwashechikovo17/earthwisefcr/blob/main/summative/linear_regression/multivariate.ipynb)
  - ⚡ **API Code Files**: [summative/API](https://github.com/kudakwashechikovo17/earthwisefcr/tree/main/summative/API)
  - 📱 **Flutter App Files**: [summative/FlutterApp](https://github.com/kudakwashechikovo17/earthwisefcr/tree/main/summative/FlutterApp)
- 🌐 **Public API (Swagger UI)**: [https://earthwise-fcr-api.onrender.com/docs](https://earthwise-fcr-api.onrender.com/docs)
- 🎥 **YouTube Video Demo**: [https://youtu.be/RR8yBmOyYdw?si=RmzA__NRK3IzpgPD](https://youtu.be/RR8yBmOyYdw?si=RmzA__NRK3IzpgPD)

---

## 1. Project Title
**Earthwise AI Poultry Production and Feed Efficiency Advisor**

---

## 2. Mission Statement and Problem Description
Earthwise aims to strengthen poultry value chains by helping smallholder farmers and cold-chain operators make better production decisions. This project predicts broiler feed efficiency (Feed Conversion Ratio - FCR) and converts the prediction into practical insights for profitability, farmer assessment, meat-yield planning, cold-storage allocation and refrigerated distribution.

---

## 3. Dataset Description
The model is trained on commercial broiler performance data stored in the repository at [`summative/linear_regression/data/poultry_data.csv`](https://github.com/kudakwashechikovo17/earthwisefcr/blob/main/summative/linear_regression/data/poultry_data.csv). Original headers in Indonesian were translated to clear English snake_case:
- `age_days` (from `Umur`): Slaughter/harvest age in days (range: 24.0 – 29.4 days)
- `body_weight_kg` (from `BW`): Average live body weight at harvest in kg (range: 0.85 – 1.51 kg)
- `harvest_percent` (from `%Panen`): Percentage of placed birds harvested (range: 5.74% – 79.77%)
- `mortality_percent` (from `Deplesi`): Cumulative flock mortality percentage (range: 1.59% – 15.49%)

---

## 4. Dataset Source and Citation
- **Repository Location**: [`summative/linear_regression/data/poultry_data.csv`](https://github.com/kudakwashechikovo17/earthwisefcr/blob/main/summative/linear_regression/data/poultry_data.csv)
- **Source**: Indonesian Commercial Broiler Flock Performance Dataset (`PS Performance.csv`).
- **Citation**: Broiler Industry Field Performance Records (Public Benchmark Data).

---

## 5. Dataset Dimensions
- **Original Rows**: 327 rows × 5 columns
- **After Deduplication**: 292 unique observations × 5 base features
- **Missing Values**: 0 (100% complete)

---

## 6. Target Variable
- **Target**: `fcr` (Feed Conversion Ratio = Feed Consumed / Body Weight Gain)
- **Derivation**: Derived from Production Index (IP) using standard industry formula:
  $$\text{FCR} = \frac{(100 - \text{mortality\_percent}) \times (\text{body\_weight\_kg} \times 1000)}{\text{production\_index} \times \text{age\_days} \times 10}$$
- **Target Summary**: Mean = 1.2314, Std = 0.1208, Min = 0.8308, Max = 1.6550.

---

## 7. Input Features
- Base Predictor Variables: `age_days`, `body_weight_kg`, `harvest_percent`, `mortality_percent`.
- *Note*: `production_index` (IP) was **dropped** to prevent direct target leakage.

---

## 8. Feature Engineering
We engineered 4 domain-specific interaction features:
1. `survival_rate` = $100 - \text{mortality\_percent}$ (Flock health indicator)
2. `weight_gain_per_day` = $\text{body\_weight\_kg} / \text{age\_days}$ (Daily growth rate)
3. `harvest_efficiency` = $\text{harvest\_percent} / \text{age\_days}$ (Turnover rate)
4. `mortality_weight_interaction` = $\text{mortality\_percent} \times \text{body\_weight\_kg}$ (Compounding mortality weight loss)

---

## 9. Visualizations and Interpretations
The notebook generates 13 visualizations stored under `summative/linear_regression/outputs/charts/`:
1. `01_fcr_distribution.png`: FCR distribution (roughly normal, mean 1.23).
2. `02_correlation_heatmap.png`: Correlation matrix showing relationships with FCR.
3. `03_bw_vs_fcr.png`: Body weight vs FCR scatter plot (heavier birds have lower FCR).
4. `04_age_vs_fcr.png`: Age vs FCR scatter plot (older birds show slight FCR increase).
5. `05_mortality_vs_fcr.png`: Mortality vs FCR scatter plot (higher mortality degrades efficiency).
6. `06_feature_distributions.png`: Histograms of all base features.
7. `07_harvest_vs_fcr.png`: Harvest percent vs FCR scatter plot.
8. `08_sgd_loss_curves.png`: SGD training and test loss curves across 200 epochs.
9. `09_model_comparison.png`: Bar chart comparing Test RMSE, MAE, R² across models.
10. `10_actual_vs_predicted.png`: Actual vs Predicted FCR scatter plot.
11. `11_residuals.png`: Residual plot around zero line.
12. `12_feature_importance.png`: Feature importance for Random Forest (`harvest_percent` & `age_days` top).
13. `13_before_after_regression.png`: Scatter plot showing data before fit and linear fit line after training.

---

## 10. Models Compared
1. **Ordinary Linear Regression (OLS)** (`LinearRegression`)
2. **Stochastic Gradient Descent** (`SGDRegressor` tuned with epoch loss tracking)
3. **Decision Tree Regressor** (`DecisionTreeRegressor` tuned with max_depth & min_samples)
4. **Random Forest Regressor** (`RandomForestRegressor` tuned with 100 estimators)

---

## 11. Evaluation Metrics Table

| Model | Train RMSE | Test RMSE | Test MAE | Test MSE | Test R² | CV RMSE | Generalization Gap |
|---|---|---|---|---|---|---|---|
| **SGD Regressor** | **0.1041** | **0.0806** | **0.0630** | **0.006494** | **0.4028** | **0.1118** | **-0.0235** |
| Linear Regression | 0.1032 | 0.0817 | 0.0634 | 0.006671 | 0.3866 | 0.1126 | -0.0215 |
| Random Forest | 0.0432 | 0.0856 | 0.0633 | 0.007332 | 0.3258 | 0.1077 | 0.0425 |
| Decision Tree | 0.0923 | 0.0995 | 0.0765 | 0.009906 | 0.0890 | 0.1136 | 0.0072 |

---

## 12. Best-Model Justification
**SGD Regressor** was selected as the best-performing model. It achieved the lowest Test RMSE (**0.0806**) and Test MAE (**0.0630**), highest Test R² (**0.4028**), and demonstrated excellent generalization with virtually zero overfitting gap between train and test performance.

---

## 13. Repository Structure

```
linear_regression_model/
├── README.md
├── .gitignore
├── VIDEO_SCRIPT.md
├── VERIFICATION_REPORT.md
└── summative/
    ├── linear_regression/
    │   ├── multivariate.ipynb
    │   ├── train_model.py
    │   ├── data/
    │   │   ├── poultry_data.csv
    │   │   └── new_training_data.csv
    │   ├── models/
    │   │   ├── best_model.joblib
    │   │   ├── preprocessor.joblib
    │   │   └── model_metadata.json
    │   └── outputs/
    │       ├── charts/
    │       └── metrics.csv
    ├── API/
    │   ├── prediction.py
    │   ├── model_service.py
    │   ├── retrain.py
    │   ├── requirements.txt
    │   └── render.yaml
    ├── FlutterApp/
    │   ├── lib/
    │   ├── test/
    │   ├── pubspec.yaml
    │   └── README.md
    ├── pyproject.toml
    └── uv.lock
```

---

## 14. How to Install with `uv`

```bash
# Clone the repository
git clone https://github.com/kudakwashechikovo17/earthwisefcr.git
cd earthwisefcr/summative

# Sync virtual environment and install dependencies
uv sync
```

---

## 15. How to Run the Notebook

```bash
# Activate environment and launch Jupyter
uv run jupyter notebook summative/linear_regression/multivariate.ipynb
```

---

## 16. How to Run the API

```bash
# Start FastAPI backend server locally
cd summative/API
uvicorn prediction:app --reload --host 0.0.0.0 --port 8000
```

---

## 17. Public Swagger URL
- **Public API Documentation**: [https://earthwise-fcr-api.onrender.com/docs](https://earthwise-fcr-api.onrender.com/docs)
- **Public Predict Endpoint**: `https://earthwise-fcr-api.onrender.com/predict`

---

## 18. How to Deploy to Render

1. Push repository to GitHub.
2. Create a new **Web Service** on [Render](https://render.com).
3. Connect your GitHub repository.
4. Set **Root Directory**: `summative/API`
5. Set **Build Command**: `pip install -r requirements.txt`
6. Set **Start Command**: `uvicorn prediction:app --host 0.0.0.0 --port $PORT`
7. Set Environment Variable: `ALLOWED_ORIGINS` = `http://localhost,http://10.0.2.2`
8. Deploy Service.

---

## 19. How to Run the Flutter App

```bash
cd summative/FlutterApp
flutter pub get
flutter run
```

---

## 20. API Request Example

`POST /predict`

```json
{
  "age_days": 27.0,
  "body_weight_kg": 1.25,
  "harvest_percent": 40.0,
  "mortality_percent": 3.5,
  "flock_size": 5000,
  "average_target_weight_kg": 2.0,
  "feed_price_rwf_per_kg": 450.0,
  "expected_selling_price_rwf_per_kg": 3500.0,
  "chick_cost_rwf_per_bird": 650.0,
  "medicine_cost_rwf": 250000.0,
  "labour_cost_rwf": 500000.0,
  "transport_cost_rwf": 150000.0,
  "other_costs_rwf": 100000.0,
  "cold_room_capacity_kg": 5000.0,
  "delivery_vehicle_capacity_kg": 2000.0,
  "dressing_yield_percent": 72.0
}
```

---

## 21. API Response Example

```json
{
  "predicted_fcr": 1.236,
  "efficiency_category": "Good — Above average feed efficiency",
  "surviving_birds": 4825.0,
  "expected_live_weight_kg": 9650.0,
  "estimated_feed_required_kg": 11927.4,
  "saleable_meat_kg": 6948.0,
  "estimated_feed_cost_rwf": 5367330.0,
  "total_production_cost_rwf": 9617330.0,
  "estimated_revenue_rwf": 24318000.0,
  "estimated_profit_rwf": 14700670.0,
  "profit_margin_percent": 60.45,
  "cold_storage_utilization_percent": 138.96,
  "delivery_trips": 4,
  "risk_level": "Low Risk",
  "contract_recommendation": "Strong candidate — Recommend for contract farming partnership",
  "disclaimer": "These are operational estimates based on the predicted FCR and user-provided cost/market assumptions..."
}
```

---

## 22. Retraining Instructions

Upload a new CSV file to `POST /retrain` via Swagger UI or cURL:
```bash
curl -X 'POST' \
  'http://localhost:8000/retrain' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@new_poultry_data.csv;type=text/csv'
```

---

## 23. CORS Justification
`CORSMiddleware` is configured using explicit environment variables (`ALLOWED_ORIGINS`). We deliberately avoided `allow_origins=["*"]` to prevent unauthorized cross-origin browser requests in production. Mobile applications bypass browser CORS policies, but Swagger UI and web browsers enforce origin security.

---

## 24. Limitations and Ethical Considerations
- **Geographic Transferability**: Trained on Indonesian broiler data; Rwandan environmental conditions, feed formulations, and breeds may vary.
- **Decision Support**: Business calculations are operational estimates and do not replace veterinary or agricultural extension services.

---

## 25. YouTube Demo Link
- **YouTube Video Demo**: [https://youtu.be/RR8yBmOyYdw?si=RmzA__NRK3IzpgPD](https://youtu.be/RR8yBmOyYdw?si=RmzA__NRK3IzpgPD)
