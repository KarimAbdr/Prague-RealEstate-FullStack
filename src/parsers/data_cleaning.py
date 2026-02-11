import pandas as pd
import numpy as np
import re
import requests
from sklearn.neighbors import NearestNeighbors
import json
import __main__
import sys
from src.services.my_classes import Encoder

from src.parsers.parser import (
    parsing_bezreality_rent_data,
    parse_sreality_rent_data,
    parsing_bezrealitky_sell_data,
    parse_sreality_sell_data
)
from src.db import init_db, get_session 
from src.db import RentListing, SellListing
    

def delete_outliers(df , column, k=1.5):
    q1 = df.groupby('disposition')[column].transform(lambda s: s.quantile(0.25))
    q3 = df.groupby('disposition')[column].transform(lambda s: s.quantile(0.75))
    iqr = q3-q1
    lo = q1 - k*iqr
    hi = q3 + k*iqr
    return df[(df[column] >= lo) & (df[column] <= hi)].copy()

def extract_district(locality):
    if pd.isna(locality):
        return None
    parts = re.split(r'\s*[-–]\s*', locality)
    return parts[-1].strip() if len(parts) > 1 else None


def normalize_disposition(val):
    mapping = {
        'GARSONIERA': '1+kk',
        'DISP_1_KK': '1+kk',
        'DISP_1_1': '1+1',
        'DISP_2_KK': '2+kk',
        'DISP_2_1': '2+1',
        'DISP_3_KK': '3+kk',
        'DISP_3_1': '3+1',
        'DISP_4_KK': '4+kk',
        'DISP_4_1': '4+1',
        'DISP_5_KK': '5+kk',
        'DISP_5_1': '5+1',
        'OSTATNI': 'other'
    }
    return mapping.get(val, val)


def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0088
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi, dlmb = np.radians(lat2 - lat1), np.radians(lon2 - lon1)
    a = np.sin(dphi/2)**2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlmb/2)**2
    return 2 * R * np.arcsin(np.sqrt(a))


def load_prague_metro_stations():
    URL = "https://data.pid.cz/stops/json/stops.json"
    try:
        raw = requests.get(URL, timeout=30).json()
        groups = pd.json_normalize(raw["stopGroups"]).rename(columns={
            "name": "station_name", "avgLat": "latitude", "avgLon": "longitude"
        })
        metro = groups[groups["mainTrafficType"].astype(str).str.contains("metro", case=False, na=False)]
        return metro[["station_name", "latitude", "longitude"]].dropna().reset_index(drop=True)
    except Exception as e:
        print(f"⚠️ Error: {e}")
        return pd.DataFrame()


def add_nearest_metro_features(df, metro_df):
    if df.empty or metro_df.empty:
        return df
    mask = df["latitude"].notna() & df["longitude"].notna()
    if not mask.any():
        return df
    
    nn = NearestNeighbors(n_neighbors=1, metric="haversine", algorithm="ball_tree")
    metro_coords = np.radians(metro_df[["latitude", "longitude"]])
    nn.fit(metro_coords)
    
    apt_coords = np.radians(df.loc[mask, ["latitude", "longitude"]])
    dist, idx = nn.kneighbors(apt_coords)
    
    df.loc[mask, "distance_to_metro_km"] = (dist.flatten() * 6371).round(1)
    df.loc[mask, "nearest_metro"] = metro_df.iloc[idx.flatten()]["station_name"].values
    
    return df


def save_to_database(df: pd.DataFrame, listing_type: str):
    session = get_session()
    Model = RentListing if listing_type == "rent" else SellListing
    
    saved_count = 0
    skipped_count = 0
    all_images_json = None
    
    for _, row in df.iterrows():
        if pd.isna(row.get("id")):
            skipped_count += 1
            continue
        if "address" in row and pd.notna(row.get("address")):
            source = "bezrealitky"
        else:
            source = "sreality"
        external_id = str(row["id"])
        
        existing = session.query(Model).filter_by(
            external_id=external_id, 
            source=source
        ).first()
        if existing:
            skipped_count += 1
            continue
        if row.get("all_images") and isinstance(row["all_images"], list):
            all_images_json = json.dumps(row["all_images"])
        
        listing = Model(
            external_id=external_id,
            source=source,
            price=int(row["price"]) if pd.notna(row.get("price")) else 0,
            price_per_m2=float(row["price_per_m2"]) if pd.notna(row.get("price_per_m2")) else None,
            disposition=row.get("disposition"),
            surface=int(row["surface"]) if pd.notna(row.get("surface")) else None,
            district=row.get("district"),
            furnishing=row.get("furnishing"),
            garage=bool(row.get("garage", False)),
            balcony=bool(row.get("balcony", False)),
            loggia=bool(row.get("loggia", False)),
            mhd=bool(row.get("mhd", False)),
            latitude=float(row["latitude"]) if pd.notna(row.get("latitude")) else None,
            longitude=float(row["longitude"]) if pd.notna(row.get("longitude")) else None,
            distance_to_center=float(row["distance_to_center"]) if pd.notna(row.get("distance_to_center")) else None,
            distance_to_metro_km=float(row["distance_to_metro_km"]) if pd.notna(row.get("distance_to_metro_km")) else None,
            nearest_metro=row.get("nearest_metro"),
            main_image=row.get("main_image"),
            all_images=all_images_json
        )
   
        session.add(listing)
        saved_count += 1    
    
    session.commit()
    
    session.close()
    
    print(f"   💾 Saved: {saved_count}, skipped bcs of dublicates: {skipped_count}")


def run_cleaning():
    print("DB initialization...")
    init_db()
    
    print("Parsing Bezrealitky rent data...")
    df_bez_rent = parsing_bezreality_rent_data()
    
    print("parsing Sreality rent data...")
    df_sre_rent = parse_sreality_rent_data(100)
    
    print("Parsing Bezrelitky sell data...")
    df_bez_sell = parsing_bezrealitky_sell_data()
    
    print("Parsing Srealitky sell data...")
    df_sre_sell = parse_sreality_sell_data(50)
    

    for df in [df_sre_rent, df_sre_sell]:
        df['district'] = df['locality'].apply(extract_district)
        df['disposition'] = df['name'].str.extract(r'(\d+\+?kk|\d+\+\d+)')
        df['surface'] = pd.to_numeric(df['name'].str.extract(r'(\d+)\s?m²')[0], errors='coerce')
    

    for df in [df_bez_rent, df_bez_sell]:
        df['district'] = df['address'].str.split('-').str[-1].str.strip()
        df['disposition'] = df['disposition'].apply(normalize_disposition)
    
 
    rent_df = pd.concat([df_bez_rent, df_sre_rent], ignore_index=True)
    sell_df = pd.concat([df_bez_sell, df_sre_sell], ignore_index=True)
    


    CBD_LAT, CBD_LON = 50.08815, 14.41585
    metro = load_prague_metro_stations()
    
    for df in [rent_df, sell_df]:
        df['price_per_m2'] = round(df['price'] / df['surface'], 1)
        
        df['distance_to_center'] = round(
            haversine_km(df["latitude"], df["longitude"], CBD_LAT, CBD_LON), 1
        )
        
        add_nearest_metro_features(df, metro)
        
        df['furnishing'] = df['furnishing'].replace({
            'partially_furnished': 'partly_furnished',
            'unknown': np.nan
        })
    
    print("Saving to DB...")

    save_to_database(rent_df, "rent")
    
    save_to_database(sell_df, "sale")
    
    return rent_df, sell_df
    

if __name__ == "__main__":
    run_cleaning()