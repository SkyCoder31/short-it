from pydantic import BaseModel
from pydantic import HttpUrl
from typing import Optional

# Incoming data from the user
class URLBase(BaseModel):
    target_url: HttpUrl
    custom_key: Optional[str] = None

class URLCreate(URLBase):
    pass

# Outgoing data to the user
class URLInfo(URLBase):
    is_active: bool
    clicks: int
    url: HttpUrl
    admin_url: HttpUrl

    class Config:
        from_attributes = True