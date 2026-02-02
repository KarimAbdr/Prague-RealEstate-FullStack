from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.db import get_session, RentListing
from sqlalchemy import func

#Count of Adverts by Disposition only for rent listings
#Average price by disposition sell and rent
#Price Distribution for rent and sell listings
#Payback period distribution for sell listings (price / predicted rent price)
router = APIRouter(prefix="/analytics", tags=["Analytics"])

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
