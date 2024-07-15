from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from urlShortener.model.urls import Url
import requests
from uuid import uuid4
from requests.exceptions import RequestException

app = FastAPI()

url_library = {}

@app.post("/shorten_url")
async def short(url: Url, short_url: str | None = None):
    data = url.model_dump()
    try:
        validated_url = requests.get(str(data["original_url"]))
        validated_url.raise_for_status()
    except RequestException:
        raise HTTPException(status_code=400, detail="Invalid URL")


    if not validated_url.status_code in range(200, 400):
        raise HTTPException(status_code=404, detail="Invalid URL")

    if short_url:
        if short_url not in url_library:
            new_url = {"short_url": short_url, **data}
            url_library[short_url] = new_url
        else:
            raise HTTPException(status_code=404, detail=f"Short URL '{short_url}' already exists.")
    else:
        short_url = str(uuid4())[:8]
        while short_url in url_library:
            short_url = str(uuid4())[:8]
        new_url = {"short_url": short_url, **data}
        url_library[short_url] = new_url
    return {"short_url": short_url}

@app.get("/list_urls")
async def listAll():
    if not url_library:
        raise HTTPException(status_code=404, detail="No URLs available.")
    return list(url_library.values())

@app.get("/redirect/{short_url}")
async def redirect(short_url: str):
    if short_url in url_library:
        redirect_link = str(url_library[short_url]["original_url"])
        print(redirect_link)
        return RedirectResponse(redirect_link, status_code=302)
    raise HTTPException(status_code=404, detail=f"No URL found for '{short_url}' short url provided.")
