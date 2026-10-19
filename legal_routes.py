from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(
    title="HumanizeAI",
    description="AI Content Humanizer API",
    version="1.0.0"
)

# Point to your templates folder (where terms.html and privacy.html live)
templates = Jinja2Templates(directory="templates")

# Optional: serve static files like CSS, images, fonts
# app.mount("/static", StaticFiles(directory="static"), name="static")


# ─────────────────────────────────────────────
#  LEGAL ROUTES
# ─────────────────────────────────────────────

@app.get("/terms", response_class=HTMLResponse, tags=["Legal"])
async def terms_and_conditions(request: Request):
    """
    Serve the Terms & Conditions page.
    URL: yoursite.com/terms
    """
    return templates.TemplateResponse("terms.html", {"request": request})


@app.get("/privacy", response_class=HTMLResponse, tags=["Legal"])
async def privacy_policy(request: Request):
    """
    Serve the Privacy Policy page.
    URL: yoursite.com/privacy
    """
    return templates.TemplateResponse("privacy.html", {"request": request})


# ─────────────────────────────────────────────
#  OPTIONAL: redirect /terms-and-conditions
#  and /privacy-policy to the short slugs
# ─────────────────────────────────────────────

from fastapi.responses import RedirectResponse

@app.get("/terms-and-conditions", include_in_schema=False)
async def terms_redirect():
    return RedirectResponse(url="/terms", status_code=301)

@app.get("/privacy-policy", include_in_schema=False)
async def privacy_redirect():
    return RedirectResponse(url="/privacy", status_code=301)



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("legal_routes:app", host="127.0.0.1", port=8000, reload=True)