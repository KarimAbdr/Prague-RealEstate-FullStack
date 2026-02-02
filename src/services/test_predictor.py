from src.services.my_classes import Encoder
from src.services.predictor import Predictor
import pandas as pd

predictor = Predictor()
test_data = {
    'surface': 50,
    'distance_to_center': 3.5,
    'distance_to_metro_km': 0.8,
    'garage': False,
    'mhd': True,
    'balcony': True,
    'loggia': False,
    'disposition': '2+kk',
    'furnishing': 'furnished',
    'district': 'Praha 1'
}

print("Testing predictor:")
try:
    result = predictor.predict(test_data)
    print(f"✅ Prediction: {result:.2f} CZK/month")
except Exception as e:
    print(f"❌ Error: {e}")

# Test with missing features
incomplete_data = {
    'surface': 60,
    'district': 'Praha 2'
    # Missing many features!
}

print("\nTesting with incomplete data:")
try:
    result = predictor.predict(incomplete_data)
    print(f"✅ Prediction: {result:.2f} CZK/month")
except Exception as e:
    print(f"❌ Error: {e}")