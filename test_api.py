import sys
import os
import json
from pathlib import Path
from fastapi.testclient import TestClient

# Add API path
sys.path.insert(0, str(Path("summative/API").resolve()))

from prediction import app

print("=" * 60)
print("RUNNING API VERIFICATION TESTS")
print("=" * 60)

with TestClient(app) as client:
    # Test 1: GET /
    r1 = client.get("/")
    print(f"1. GET / -> Status: {r1.status_code}")
    assert r1.status_code == 200, f"Failed GET /: {r1.text}"
    print(f"   Body: {r1.json()['api_name']} - Status: {r1.json()['status']}")

    # Test 2: GET /health
    r2 = client.get("/health")
    print(f"2. GET /health -> Status: {r2.status_code}")
    assert r2.status_code == 200, f"Failed GET /health: {r2.text}"
    print(f"   Model: {r2.json()['model_name']} v{r2.json()['model_version']}")

    # Test 3: GET /model-info
    r3 = client.get("/model-info")
    print(f"3. GET /model-info -> Status: {r3.status_code}")
    assert r3.status_code == 200, f"Failed GET /model-info: {r3.text}"
    print(f"   Target: {r3.json()['target']}, Test RMSE: {r3.json()['metrics']['test_rmse']}")

    # Test 4: POST /predict (valid data)
    valid_payload = {
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
    r4 = client.post("/predict", json=valid_payload)
    print(f"4. POST /predict (valid) -> Status: {r4.status_code}")
    assert r4.status_code == 200, f"Failed POST /predict: {r4.text}"
    res = r4.json()
    print(f"   Predicted FCR: {res['predicted_fcr']}")
    print(f"   Efficiency: {res['efficiency_category']}")
    print(f"   Estimated Profit: RWF {res['estimated_profit_rwf']:,}")

    # Test 5: POST /predict (out of range mortality)
    invalid_payload_range = dict(valid_payload)
    invalid_payload_range["mortality_percent"] = 150.0 # max is 50
    r5 = client.post("/predict", json=invalid_payload_range)
    print(f"5. POST /predict (out of range) -> Status: {r5.status_code} (Expected 422)")
    assert r5.status_code == 422

    # Test 6: POST /predict (missing required field)
    invalid_payload_missing = dict(valid_payload)
    del invalid_payload_missing["flock_size"]
    r6 = client.post("/predict", json=invalid_payload_missing)
    print(f"6. POST /predict (missing field) -> Status: {r6.status_code} (Expected 422)")
    assert r6.status_code == 422

    # Test 7: POST /predict (wrong data type)
    invalid_payload_type = dict(valid_payload)
    invalid_payload_type["age_days"] = "twenty-seven"
    r7 = client.post("/predict", json=invalid_payload_type)
    print(f"7. POST /predict (wrong type) -> Status: {r7.status_code} (Expected 422)")
    assert r7.status_code == 422

    # Test 8: POST /retrain with valid CSV (15 unique rows)
    csv_data = "age_days,body_weight_kg,harvest_percent,mortality_percent,production_index\n"
    for i in range(15):
        csv_data += f"{25.0 + i*0.2},{1.0 + i*0.03},{30.0 + i},{2.0 + i*0.1},{300.0 + i*5}\n"

    files = {"file": ("test_retrain.csv", csv_data.encode('utf-8'), "text/csv")}
    r8 = client.post("/retrain", files=files)
    print(f"8. POST /retrain (valid CSV) -> Status: {r8.status_code}")
    assert r8.status_code == 200, f"Failed POST /retrain: {r8.text}"
    print(f"   Message: {r8.json()['message']}")
    print(f"   Best Model: {r8.json()['best_model']}")

print("=" * 60)
print("ALL API VERIFICATION TESTS PASSED SUCCESSFULLY!")
print("=" * 60)

print("=" * 60)
print("ALL API VERIFICATION TESTS PASSED SUCCESSFULLY!")
print("=" * 60)
