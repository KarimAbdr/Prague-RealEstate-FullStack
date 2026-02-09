import json
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from src.db import get_session, SellListing
from src.schemas.listing import SellListingRead

router = APIRouter(prefix="/api/marketplace", tags=["Marketplace"])


def get_db():
    """Database session dependency"""
    db = get_session()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=List[SellListingRead])
def get_marketplace_listings(
    district: Optional[str] = Query(None, description="Filter by district"),
    min_price: Optional[int] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[int] = Query(None, ge=0, description="Maximum price"),
    disposition: Optional[str] = Query(None, description="Disposition filter (e.g., 2+kk)"),
    
    skip: int = Query(0, ge=0, description="Skip N records"),
    limit: int = Query(20, le=100, description="Maximum number of records to return"),
    
    db: Session = Depends(get_db)
):
    """
    Get apartments for sale with filters and pagination
    
    Examples:
    - /api/marketplace/ - first 20 apartments
    - /api/marketplace/?limit=50 - first 50 apartments
    - /api/marketplace/?district=Praha 1 - only Praha 1
    - /api/marketplace/?min_price=3000000&max_price=6000000 - by price range
    - /api/marketplace/?skip=20&limit=20 - next 20 (page 2)
    """
    
    query = db.query(SellListing)
    query = query.filter(SellListing.price >= 500000)
    if district:
        query = query.filter(SellListing.district == district)
    
    if min_price:
        query = query.filter(SellListing.price >= min_price)
    
    if max_price:
        query = query.filter(SellListing.price <= max_price)
    
    if disposition:
        query = query.filter(SellListing.disposition == disposition)
    
    # Only apartments with predicted rent price
    query = query.filter(SellListing.predicted_rent_price.isnot(None))
    
    # Sort by price (cheapest first)
    query = query.order_by(SellListing.price.asc())
    
    # Pagination
    listings = query.offset(skip).limit(limit).all()
    
    # Convert to dict and calculate ROI
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
        
        # Parse all_images from JSON string to list
        if listing.all_images:
            try:
                listing_dict["all_images"] = json.loads(listing.all_images)
            except Exception as e:
                print(f"Error parsing all_images for listing {listing.id}: {e}")
                listing_dict["all_images"] = []
        else:
            listing_dict["all_images"] = []
        
        # Calculate Years to Payback (ROI)
        if listing.predicted_rent_price and listing.predicted_rent_price > 0:
            annual_rent = listing.predicted_rent_price * 12
            years_to_payback = listing.price / annual_rent
            listing_dict["years_to_payback"] = round(years_to_payback, 1)
        else:
            listing_dict["years_to_payback"] = None
        
        result.append(listing_dict)
    
    return result

@router.get("/districts")
def get_unique_districts(db: Session = Depends(get_db)):
    """
    Get all unique districts from database
    Returns sorted list of districts
    """
    # Query unique districts (только непустые)
    districts = db.query(SellListing.district)\
        .filter(SellListing.district.isnot(None))\
        .filter(SellListing.district != "")\
        .distinct()\
        .order_by(SellListing.district.asc())\
        .all()
    
    # Преобразуем из [(district,), (district,)] в [district, district]
    district_list = [row[0] for row in districts if row[0]]
    
    return {
        "districts": district_list,
        "total": len(district_list)
    }

@router.get("/dispositions")
def get_unique_dispositions(db: Session = Depends(get_db)):
    dispositions = [
        "1+kk",
        "1+1",
        "2+kk",
        "2+1",
        "3+kk",
        "3+1",
        "4+kk",
        "4+1",
        "5+kk",
        "5+1",
        "6+kk",
        "6+1"
        ]
    return {
        "dispositions": dispositions,
        "total": len(dispositions)
    }
