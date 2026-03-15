import hashlib
from datetime import date
from pathlib import Path

import frontmatter
import markdown
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(title="bananabread.blog")

app.mount("/static", StaticFiles(directory="app/web/static"), name="static")
templates = Jinja2Templates(directory="app/web/templates")

CONTENT_DIR = Path("content")


def _css_version() -> str:
    """Hash of styles.css for cache busting."""
    path = "app/web/static/css/styles.css"
    try:
        with open(path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()[:8]
    except FileNotFoundError:
        return "0"


CSS_VERSION = _css_version()


def _load_articles() -> list[dict]:
    """Load all markdown articles from content/ and return sorted by date descending."""
    articles = []
    if not CONTENT_DIR.exists():
        return articles
    for path in CONTENT_DIR.glob("*.md"):
        post = frontmatter.load(path)
        articles.append({
            "slug": path.stem,
            "title": post.get("title", path.stem),
            "date": post.get("date", date.today()),
            "category": post.get("category", ""),
            "excerpt": post.get("excerpt", ""),
            "body": post.content,
        })
    articles.sort(key=lambda a: a["date"], reverse=True)
    return articles


ARTICLES = _load_articles()


def get_date() -> str:
    return date.today().strftime("%A, %-d %B %Y")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={"date": get_date(), "version": CSS_VERSION, "articles": ARTICLES},
    )


@app.get("/articles", response_class=HTMLResponse)
async def article_list(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="articles.html",
        context={"date": get_date(), "version": CSS_VERSION, "articles": ARTICLES},
    )


@app.get("/articles/{slug}", response_class=HTMLResponse)
async def article_detail(request: Request, slug: str):
    article = next((a for a in ARTICLES if a["slug"] == slug), None)
    if article is None:
        return HTMLResponse(status_code=404, content="Article not found")
    body_html = markdown.markdown(article["body"])
    return templates.TemplateResponse(
        request=request,
        name="article.html",
        context={
            "date": get_date(),
            "version": CSS_VERSION,
            "article": article,
            "body_html": body_html,
        },
    )
