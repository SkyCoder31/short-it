from sqlalchemy.orm import Session
from src import models
import httpx

def record_click_stats(url_key: str, ip: str, user_agent: str, db: Session):
    """
    Background task to record click analytics with Geo-Location.
    """
    country = "Unknown"
    city = "Unknown"
    if ip != "127.0.0.1" and ip != "localhost":
        try:
            # We use a timeout so our background task doesn't hang forever
            response = httpx.get(f"http://ip-api.com/json/{ip}", timeout=3.0)
            data = response.json()
            if data.get("status") == "success":
                country = data.get("country", "Unknown")
                city = data.get("city", "Unknown")
        except Exception as e:
            print(f"Geo-lookup failed: {e}")

    try:
        db_url = db.query(models.URL).filter(models.URL.key == url_key).first()
        
        if db_url:
            db_url.clicks += 1 # type: ignore
            
            click_entry = models.Click(
                url_key=url_key,
                client_ip=ip,
                user_agent=user_agent,
                country=country,
                city=city
            )
            
            db.add(click_entry)
            db.commit()
            
    except Exception as e:
        print(f"Failed to log click: {e}")
    finally:
        db.close()