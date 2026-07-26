# Video Demonstration Timed Script (7 Minutes Maximum)

**Presenter:** Student / Lead ML Engineer  
**Camera Requirement:** Camera MUST be ON the entire duration  
**Screen Requirement:** Full Screen MUST be shared  

---

## Timed Schedule & Script

### 0:00 – 0:20 | Introduction & Mission
- **Screen:** Title slide or IDE showing the project workspace.
- **Presenter Camera:** ON.
- **Script:** "Hello! Welcome to the demonstration of the Earthwise AI Poultry Production and Feed Efficiency Advisor. Earthwise is a Rwandan agritech and cold-chain company. Our mission is to strengthen poultry value chains by predicting broiler Feed Conversion Ratio (FCR) and translating that prediction into operational decision-support for profitability, risk assessment, cold storage allocation, and refrigerated transport."

### 0:20 – 1:00 | Mobile App Live Prediction Demo
- **Screen:** Flutter Mobile App running on Android Emulator or physical device.
- **Script:** "Here is our Flutter mobile application, 'Earthwise Poultry Advisor'. Notice the clean agricultural design system with dark green, white, and warm gold accents. The screen is divided into clear sections: Farm Performance, Farm & Cost Information, and Market & Logistics. I will input a harvest age of 27 days, body weight of 1.25 kg, harvest percentage of 40%, mortality of 3.5%, and a flock size of 5,000 birds. When I click 'Predict', the app sends a POST request to our FastAPI backend. Instantly, we see our results formatted in RWF: predicted FCR of 1.236, 'Good' efficiency, expected profit of RWF 14.7M, cold storage utilization of 138.9%, 4 delivery trips required, and a 'Low Risk' rating for contract farming."

### 1:00 – 2:00 | FastAPI & Swagger UI Endpoint Tests
- **Screen:** Browser open to Swagger UI (`/docs`).
- **Script:** "Now let's test our API on Swagger UI. 
  1. First, a valid `/predict` request with JSON data. Executing this returns HTTP 200 with the exact FCR prediction and calculated business estimates.
  2. Next, testing data type validation: I'll pass a string `"twenty"` for `age_days`. The API returns HTTP 422 Unprocessable Entity with a clear Pydantic error message.
  3. Third, testing range constraints: Setting `mortality_percent` to `-10%` or `150%` triggers Pydantic's field validation, blocking out-of-bounds numbers.
  4. Fourth, omitting a required field like `flock_size` correctly yields an HTTP 422 error detailing the missing field."

### 2:00 – 3:15 | Jupyter Notebook & Data Exploration
- **Screen:** `summative/linear_regression/multivariate.ipynb`.
- **Script:** "Let's examine our ML development notebook. We loaded 327 commercial broiler performance observations from Kaggle/data source. We identified 35 duplicate rows and dropped them. Original columns were in Indonesian (`Umur`, `BW`, `%Panen`, `Deplesi`, `IP`). We translated them to English snake_case and derived FCR using the standard Production Index formula: FCR = (Livability% × BW_grams) / (IP × Age_days × 10). To prevent target leakage, `production_index` (IP) was completely excluded from predictor features. Here are our 13 visualizations including FCR distribution, correlation heatmaps, body weight vs. FCR scatter plots, and engineered features like `weight_gain_per_day` and `survival_rate`."

### 3:15 – 4:30 | Model Comparison & Performance Metrics
- **Screen:** Notebook section with model comparison table and bar charts.
- **Script:** "We evaluated four regression models using an 80/20 train-test split:
  1. Ordinary Linear Regression (OLS)
  2. Stochastic Gradient Descent (SGDRegressor)
  3. Decision Tree Regressor
  4. Random Forest Regressor
  Our primary selection metric is lowest test RMSE. Comparing models:
  - SGD Regressor achieved Test RMSE of 0.0806, Test MAE of 0.0630, and Test R² of 0.4028.
  - Linear Regression achieved Test RMSE of 0.0817 and R² of 0.3866.
  - Random Forest achieved Test RMSE of 0.0856 and R² of 0.3258.
  - Decision Tree suffered from overfitting on un-tuned depth, achieving higher error.
  SGD Regressor was selected as our best model due to superior test RMSE and generalization capability."

### 4:30 – 5:15 | Loss Curves & Key Questions
- **Screen:** Chart `08_sgd_loss_curves.png` showing SGD training and test loss across epochs.
- **Script:** "Here are the SGD loss curves across 200 epochs. 
  - **Is the Loss High or Low?** The test MSE is 0.0065 (RMSE 0.0806 on an FCR range of 0.83–1.65), which represents an average error of only ~0.06 FCR points. This loss is relatively low and acceptable for commercial flock management.
  - **How to further reduce loss?** We could collect farm-level environmental data (temperature, humidity, feed protein %), increase dataset size beyond 292 unique rows, and collect feed consumption directly rather than deriving FCR from IP."

### 5:15 – 5:50 | Hyperparameters & Model Selection
- **Screen:** Code showing `RandomizedSearchCV` and model metadata JSON.
- **Script:** "
  - **Hyperparameters:** For SGD, hyperparameters like `alpha` (L2 regularization strength), `learning_rate` ('invscaling' vs 'constant'), `eta0` (initial learning rate), and `penalty` directly control convergence and prevent overfitting. For Random Forest, `n_estimators`, `max_depth`, `min_samples_split`, and `max_features` tune tree complexity."

### 5:50 – 6:20 | Model Updating & Retraining API Demonstration
- **Screen:** Postman / cURL / Swagger UI testing `/retrain`.
- **Script:** "
  - **What happens with new data?** Our API features a `/retrain` endpoint. When new flock data is uploaded as CSV, the system validates schema and ranges, backs up the active model, retrains all 4 candidate models, evaluates them on a holdout set, and atomically swaps the active model only if the new model performs cleanly. If retraining fails or metrics degrade, the previous model is retained."

### 6:20 – 6:45 | CORS Configuration Justification
- **Screen:** `prediction.py` CORS middleware code snippet.
- **Script:** "
  - **CORS Basis:** We configured `CORSMiddleware` with explicit allowed origins read from the `ALLOWED_ORIGINS` environment variable (defaulting to localhost and mobile emulator IPs), explicitly avoiding wildcard `allow_origins=['*']`. Mobile Flutter apps bypass browser CORS, but Swagger UI and web clients do not. Restricting origins prevents cross-site request forgery and unauthorized browser access."

### 6:45 – 7:00 | Conclusion
- **Screen:** Flutter App final screen / GitHub repository structure.
- **Script:** "In conclusion, Earthwise AI provides a robust, end-to-end ML deployment pipeline—from rigorous dataset cleaning and multivariate modeling to a hosted FastAPI backend and a responsive Flutter app. Thank you!"
