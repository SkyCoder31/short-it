from datetime import datetime
from pydantic import BaseModel
from pydantic import HttpUrl
from typing import Optional,List

# Incoming data from the user
class URLBase(BaseModel):
    target_url: HttpUrl
    custom_key: Optional[str] = None

class URLCreate(URLBase):
    pass

class ClickInfo(BaseModel):
    timestamp: datetime
    country: str
    city: str
    client_ip: str

    class Config:
        from_attributes = True
# Outgoing data to the user
class URLInfo(URLBase):
    key: str
    is_active: bool
    clicks: int
    url: HttpUrl
    admin_url: HttpUrl
    click_events: List[ClickInfo] = []

    class Config:
        from_attributes = True