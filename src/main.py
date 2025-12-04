from contextlib import asynccontextmanager
from io import BytesIO

import qrcode
import qrcode.constants
import redis
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, StreamingResponse
from sqlalchemy.orm import Session

from src import keygen, models, schemas
from src.config import get_settings
from src.database import SessionLocal, engine, get_db
from src.services import analytics


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up...")
    models.Base.metadata.create_all(bind=engine)
    yield
    print("Shutting down...")

settings = get_settings()
redis_client = redis.Redis.from_url(settings.redis_url, decode_responses=True)

app = FastAPI(title="URL Shortener API", lifespan=lifespan)

origins = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "https://short-it-rosy.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {
        "message": "Welcome to the URL Shortener API"
    }


@app.post("/url", response_model=schemas.URLInfo)
def create_url(url: schemas.URLCreate, request: Request, db: Session = Depends(get_db)):
    client_ip = request.client.host if request.client else "127.0.0.1"
    limit_key = f"rate_limit:{client_ip}"
    current_count = redis_client.get(limit_key)

    # limiting the requests per ip
    if current_count and int(str(current_count)) >= 5:
        raise HTTPException(status_code=429, detail="Too many requests. Slow down!")

    # Increment the counter
    redis_client.incr(limit_key)

    # Set expiration time (60 seconds)
    if current_count is None:
        redis_client.expire(limit_key, 60)

    if url.custom_key:
        if db.query(models.URL).filter(models.URL.key == url.custom_key).first():
            raise HTTPException(status_code=400, detail="Custom alias already exists")
        key = url.custom_key
    else:
        key = keygen.create_random_key()

    secret_key = keygen.create_random_key(length=8)

    db_url = models.URL(target_url=str(url.target_url), key=key, secret_key=secret_key)

    db.add(db_url)
    db.commit()
    db.refresh(db_url)

    db_url.url = str(request.base_url) + key
    db_url.admin_url = str(request.base_url) + "admin/" + secret_key

    return db_url


@app.get("/{url_key}")
def forward_to_target_url(
    url_key: str,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    # fetching from cache first
    cache_data = redis_client.get(f"url:{url_key}")

    if cache_data:
        background_tasks.add_task(
            analytics.record_click_stats,
            url_key,
            request.client.host if request.client else "127.0.0.1",
            request.headers.get("user-agent", "Unknown"),
            SessionLocal(),  # Pass a fresh DB session
        )
        # Still count the click in DB asynchronously
        return RedirectResponse(str(cache_data))

    db_url = (
        db.query(models.URL)
        .filter(models.URL.key == url_key, models.URL.is_active.is_(True))
        .first()
    )

    if db_url:
        # if not in cache, store it
        redis_client.set(f"url:{url_key}", str(db_url.target_url), ex=10800)

        # updating click count
        # Note: In a real massive system, we would move this to a background task
        db_url.clicks += 1  # type: ignore

        # Log event
        click_entry = models.Click(
            url_key=url_key,
            client_ip=request.client.host if request.client else "Unknown",
            user_agent=request.headers.get("user-agent", "Unknown"),
        )
        db.add(click_entry)
        db.commit()

        return RedirectResponse(str(db_url.target_url))
    else:
        raise HTTPException(status_code=404, detail="URL not found")


@app.get("/{url_key}/qr")
def generate_qr(url_key: str, request: Request, db: Session = Depends(get_db)):
    # search url in db
    db_url = (
        db.query(models.URL)
        .filter(models.URL.key == url_key, models.URL.is_active.is_(True))
        .first()
    )

    if not db_url:
        raise HTTPException(status_code=404, detail="URL not found")

    # reconstruct full URL
    full_url = str(request.base_url) + url_key

    # QR code generation
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(full_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Save image to a memory buffer
    buf = BytesIO()
    img.save(buf)
    buf.seek(0)

    # Actual QR
    return StreamingResponse(buf, media_type="image/png")


@app.get("/admin/{secret_key}", response_model=schemas.URLInfo)
def get_url_info(secret_key: str, request: Request, db: Session = Depends(get_db)):
    db_url = (
        db.query(models.URL)
        .filter(models.URL.secret_key == secret_key, models.URL.is_active.is_(True))
        .first()
    )

    if not db_url:
        raise HTTPException(status_code=404, detail="URL not found")

    # Reconstruct the full URLs
    db_url.url = str(request.base_url) + db_url.key
    db_url.admin_url = str(request.base_url) + "admin/" + db_url.secret_key

    return db_url
