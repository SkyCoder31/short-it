from sqlalchemy.orm import Session
from src import models

def record_click_stats(url_key: str, ip: str, user_agent: str, db: Session):
    """
    Background task to record click analytics.
    This runs independently of the main API request.
    """
    try:
        db_url = db.query(models.URL).filter(models.URL.key == url_key).first()
        
        if db_url:
            db_url.clicks += 1 # type: ignore
            
            click_entry = models.Click(
                url_key=url_key,
                client_ip=ip,
                user_agent=user_agent
            )
            
            db.add(click_entry)
            db.commit()
            
    except Exception as e:
        print(f"Failed to log click: {e}")
    finally:
        # Important this one! Close the database session created for this background task
        db.close()