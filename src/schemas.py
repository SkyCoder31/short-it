from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, HttpUrl


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

    model_config = ConfigDict(from_attributes=True)

# Outgoing data to the user
class URLInfo(URLBase):
    key: str
    is_active: bool
    clicks: int
    url: HttpUrl
    admin_url: HttpUrl
    click_events: List[ClickInfo] = []

    model_config = ConfigDict(from_attributes=True)
