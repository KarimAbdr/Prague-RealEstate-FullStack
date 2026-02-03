import json
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from src.db import get_session, SellListing
from src.schemas.listing import SellListingRead

router = APIRouter(prefix="/api", tags=["Marketplace"])

def get_db():
    db = get_session()
    try:
        yield db
    finally:
        db.close()

@router.get("/marketplace", response_model=List[SellListingRead])
def get_marketplace_listings(
    district: Optional[str] = Query(None, description="Filter by district"),
    min_price: Optional[int] = Query(None, ge=0, description="Mininal price"),
    max_price: Optional[int] = Query(None, ge=0, description="Maximal price"),
    disposition: Optional[str] = Query(None, description="Disposition filter"),
    
    skip: int = Query(0, ge=0, description="Skip number of records"),
    limit: int = Query(20, le=100, description="Maximal number of records to return"),
    
    db: Session = Depends(get_db)
):
    
    query = db.query(SellListing)
    
    if district:
        query = query.filter(SellListing.district == district)
    
    if min_price:
        query = query.filter(SellListing.price >= min_price)
    
    if max_price:
        query = query.filter(SellListing.price <= max_price)
    
    if disposition:
        query = query.filter(SellListing.disposition == disposition)
    
    query = query.filter(SellListing.predicted_rent_price.isnot(None))
    
    query = query.order_by(SellListing.price.asc())
    
    listings = query.offset(skip).limit(limit).all()
    
    result = []
    for listing in listings:
        listing_dict = {
            "id": listing.id,
            "price": listing.price,
            "disposition": listing.disposition,
            "surface": listing.surface,
            "district": listing.district,
            "furnishing": listing.furnishing,
            "latitude": listing.latitude,
            "longitude": listing.longitude,
            "distance_to_center": listing.distance_to_center,
            "distance_to_metro_km": listing.distance_to_metro_km,
            "nearest_metro": listing.nearest_metro,
            "main_image": listing.main_image,  
            "predicted_rent_price": listing.predicted_rent_price,
        }
        
        if listing.all_images:
            try:
                listing_dict["all_images"] = json.loads(listing.all_images)
            except:
                listing_dict["all_images"] = []
        else:
            listing_dict["all_images"] = []
        
        if listing.predicted_rent_price and listing.predicted_rent_price > 0:
            annual_rent = listing.predicted_rent_price * 12  
            years_to_payback = listing.price / annual_rent   
            listing_dict["years_to_payback"] = round(years_to_payback, 1)
        else:
            listing_dict["years_to_payback"] = None
        
        result.append(listing_dict)
    
    return result