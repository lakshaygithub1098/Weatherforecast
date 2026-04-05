import urllib.request
import json

req = urllib.request.Request(
    'http://localhost:8000/predict',
    data=json.dumps({'latitude': 28.55, 'longitude': 77.23, 'station_name': 'ITO'}).encode(),
    headers={'Content-Type': 'application/json'},
    method='POST'
)

try:
    resp = urllib.request.urlopen(req)
    data = json.loads(resp.read().decode())
    print('API Response:')
    print(f"  AQI: {data['aqi']:.1f}")
    print(f"  XGBoost: {data['xgboost_prediction']:.1f}")
    print(f"  LSTM: {data['lstm_prediction']:.1f}")
    print(f"  Confidence XGB: {data['model_confidence']['xgboost']:.2f}")
    print(f"  Status: SUCCESS!")
except Exception as e:
    print(f"ERROR: {e}")
