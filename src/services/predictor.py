import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from src.services.my_classes import Encoder
class Predictor:
    def __init__(self):
        self.features = ["surface", "distance_to_center", "distance_to_metro_km","garage", "mhd", "balcony", "loggia",
                         "disposition", "furnishing", "district"]
        self.base_dir = Path(__file__).resolve().parent.parent.parent
        self.regressor_path = self.base_dir / "models" / "rent_regressor_pipeline.joblib"
        self.model = None
        self.load_model()
    
    def load_model(self):
        try:
            self.model = joblib.load(self.regressor_path)
            print(f"✅ Model loaded from {self.regressor_path}")
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            self.model = None
    
    def predict(self, data):
        df = pd.DataFrame([data])
        df = df[self.features]
        prediction = self.model.predict(df)
        return float(prediction[0])



