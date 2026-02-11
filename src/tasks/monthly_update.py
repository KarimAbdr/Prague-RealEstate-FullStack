import logging
from datetime import datetime
from src.parsers.data_cleaning import run_cleaning

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def monthly_data_update():
    logger.info("=" * 60)
    logger.info(f"MONTHLY UPDATE STARTED at {datetime.now()}")
    logger.info("=" * 60)
    
    try:
        rent_df, sell_df = run_cleaning()
        
        logger.info(f"✅ Rent listings processed: {len(rent_df)}")
        logger.info(f"✅ Sell listings processed: {len(sell_df)}")
        logger.info("✅ Monthly update completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Monthly update FAILED: {e}")
        raise

if __name__ == "__main__":
    monthly_data_update()