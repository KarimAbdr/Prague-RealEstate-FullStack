from src.db import get_session , SellListing
from src.services.predictor import Predictor
import pandas as pd
from src.services.my_classes import Encoder

session = get_session()
predictor = Predictor()

listings = session.query(SellListing).all()

data = []
for listing in listings:
    data.append({
        "id": listing.id,
        "surface": listing.surface,
        "distance_to_center": listing.distance_to_center,
        "distance_to_metro_km": listing.distance_to_metro_km,
        "garage": listing.garage, 
        "mhd": listing.mhd,
        "balcony": listing.balcony,
        "loggia": listing.loggia,
        "disposition": listing.disposition,
        "furnishing": listing.furnishing,
        "district": listing.district
    })

df = pd.DataFrame(data)
features = ["surface", "distance_to_center", "distance_to_metro_km","garage", "mhd", "balcony", "loggia",
         "disposition", "furnishing", "district"]
X = df[features]
df['predicted_rent_price'] = predictor.model.predict(X).round(2)
for _, row in df.iterrows():
    listing = session.query(SellListing).filter_by(id=row['id']).first()
    listing.predicted_rent_price = float(row['predicted_rent_price'])
session.commit()
session.close()

print("Predicted rent prices added to sell listings , number of listings updated:", len(df))
