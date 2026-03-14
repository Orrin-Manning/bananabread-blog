import hashlib
import os
from datetime import date

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(title="bananabread.blog")

app.mount("/static", StaticFiles(directory="app/web/static"), name="static")
templates = Jinja2Templates(directory="app/web/templates")


def _css_version() -> str:
    """Hash of styles.css for cache busting."""
    path = "app/web/static/css/styles.css"
    try:
        with open(path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()[:8]
    except FileNotFoundError:
        return "0"


CSS_VERSION = _css_version()


def get_date() -> str:
    return date.today().strftime("%A, %-d %B %Y")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={"date": get_date(), "version": CSS_VERSION},
    )
