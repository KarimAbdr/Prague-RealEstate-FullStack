from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.db import get_session, RentListing, SellListing
from sqlalchemy import func
import numpy as np

#Count of Adverts by Disposition only for rent listings done
#Average price by disposition sell and rent (rent done)
#Price Distribution for rent and sell listings
#Payback period distribution for sell listings (price / predicted rent price)
router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

def get_db():
    db = get_session()
    try:
        yield db
    finally:
        db.close()

@router.get("/count_by_disposition")
def count_by_disposition(db: Session = Depends(get_db)):
    results = db.query(
        RentListing.disposition,
        func.count(RentListing.id).label("count")
    ).group_by(RentListing.disposition).order_by(func.count(RentListing.id).desc()).all()
    return {
        "labels":[row.disposition for row in results if row.disposition],
        "values":[row.count for row in results if row.disposition]
    }

@router.get("/average_price")
def average_price(db: Session = Depends(get_db)):
    results = db.query(
        RentListing.disposition,
        func.avg(RentListing.price).label("average_price")
    ).group_by(RentListing.disposition).all()
    return{
        "labels":[row.disposition for row in results if row.disposition],
        "values":[round(row.average_price,2) for row in results if row.disposition]
    }

@router.get("/price_distribution_rent")
def price_distribution(db: Session = Depends(get_db)):
    results = db.query(RentListing.price).all()
    prices = [row.price for row in results if row.price]
    
    if not prices:
        return {"labels": [], "values": []}
    
    prices_array = np.array(prices)
    
    percentile_99 = np.percentile(prices_array, 99)
    
   
    prices_filtered = prices_array[prices_array <= percentile_99]
    
    min_price = prices_filtered.min()
    max_price = prices_filtered.max()
    

    bin_size = 5000
    
 
    min_rounded = int(np.floor(min_price / bin_size) * bin_size)
    max_rounded = int(np.ceil(max_price / bin_size) * bin_size)
    
  
    if (max_rounded - min_rounded) / bin_size > 15:
        max_rounded = min_rounded + (15 * bin_size)
    
  
    bins = np.arange(min_rounded, max_rounded + bin_size, bin_size)
    
    hist, bin_edges = np.histogram(prices_array, bins=bins)
    
    labels = []
    for i in range(len(bin_edges) - 1):
        start = int(bin_edges[i])
        end = int(bin_edges[i+1])
        labels.append(f"{start:,} - {end:,}".replace(",", " "))
    
    return {
        "labels": labels,
        "values": hist.tolist(),
        "total": len(prices),                   
        "min": int(prices_array.min()),         
        "max": int(prices_array.max()),         
        "avg": int(prices_array.mean())    
    }

@router.get("/price_distribution_sell")
def price_distribution_sell(db: Session = Depends(get_db)):
    results = db.query(SellListing.price).all()
    prices = [row.price for row in results if row.price]
    
    if not prices:
        return {"labels": [], "values": []}
    
    prices_array = np.array(prices)
    
    percentile_99 = np.percentile(prices_array, 99)
    prices_filtered = prices_array[prices_array <= percentile_99]
    
    min_price = prices_filtered.min()
    max_price = prices_filtered.max()
    
    
    price_range = max_price - min_price
    
    if price_range <= 5_000_000:
        bin_size = 500_000      
    elif price_range <= 10_000_000:
        bin_size = 1_000_000   
    else:
        bin_size = 2_000_000    
    
    min_rounded = int(np.floor(min_price / bin_size) * bin_size)
    max_rounded = int(np.ceil(max_price / bin_size) * bin_size)
    
   
    if (max_rounded - min_rounded) / bin_size > 15:
        max_rounded = min_rounded + (15 * bin_size)
    
    bins = np.arange(min_rounded, max_rounded + bin_size, bin_size)
    
   
    hist, bin_edges = np.histogram(prices_array, bins=bins)
    
  
    labels = []
    for i in range(len(bin_edges) - 1):
        start = int(bin_edges[i])
        end = int(bin_edges[i+1])
        
        
        if start >= 1_000_000:
            start_label = f"{start/1_000_000:.1f}M"
            end_label = f"{end/1_000_000:.1f}M"
            labels.append(f"{start_label} - {end_label}")
        else:
            labels.append(f"{start:,} - {end:,}".replace(",", " "))
    
    return {
        "labels": labels,
        "values": hist.tolist(),
        "total": len(prices),
        "min": int(prices_array.min()),
        "max": int(prices_array.max()),
        "avg": int(prices_array.mean())
    }

@router.get("/payback_period_distribution")
def payback_period_distribution(db: Session = Depends(get_db)):
    results = db.query(SellListing.price , SellListing.predicted_rent_price).all()
    payback_periods = []
    for price, rent_price in results:
        if price and rent_price and rent_price > 0:
            anual_price = price/(rent_price * 12)
            payback_periods.append(round(anual_price,1))
    
