from pydantic import BaseModel, HttpUrl, field_validator
from fastapi import HTTPException
from urllib.parse import urlparse

class Url(BaseModel):
    original_url: HttpUrl

    @field_validator('original_url', mode="before")
    def valid_url(cls, url):
        parsed_url = urlparse(url)
        if not parsed_url.scheme:
            raise HTTPException(status_code=400, detail="Value must start 'http://' or 'https://'")
        return url
