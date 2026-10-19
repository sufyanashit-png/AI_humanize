from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os
from mangum import Mangum

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
TEMPLATES_DIR = os.path.join(PROJECT_ROOT, "templates")

print(f"[DEBUG] BASE_DIR: {BASE_DIR}")
print(f"[DEBUG] PROJECT_ROOT: {PROJECT_ROOT}")
print(f"[DEBUG] TEMPLATES_DIR: {TEMPLATES_DIR}")
print(f"[DEBUG] Templates exist: {os.path.exists(TEMPLATES_DIR)}")
if os.path.exists(TEMPLATES_DIR):
    print(f"[DEBUG] Templates contents: {os.listdir(TEMPLATES_DIR)}")

app = FastAPI(
    title="HumanizeAI",
    description="AI Content Humanizer API",
    version="1.0.0"
)

templates = Jinja2Templates(directory=TEMPLATES_DIR)

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.7
)

humanize_prompt = ChatPromptTemplate.from_messages([
    ("system",
     """You are an AI Humanizer.
     Your task is to rewrite any given text so it sounds natural,
     conversational, and written by a human. Avoid robotic tone.
     Keep the meaning the same but improve flow, readability,
     and human-like expression."""),
    ("human", "{text}")
])

synonyms_prompt = ChatPromptTemplate.from_messages([
    ("system",
     """You are a synonym generator.
        When given a single word, return a list of possible synonyms for that word.
        Only output the synonyms, separated by commas. Do not include explanations, sentences, or any additional text."""),
    ("human", "{text}")
])

parser = StrOutputParser()
humanize_chain = humanize_prompt | llm | parser
synonyms_chain = synonyms_prompt | llm | parser


class PromptRequest(BaseModel):
    prompt: str


@app.post("/humanize")
def humanize_text(request: PromptRequest):
    response = humanize_chain.invoke({"text": request.prompt})
    return {"original": request.prompt, "humanized": response}


@app.post("/synonyms")
def synonym_generator(request: PromptRequest):
    response = synonyms_chain.invoke({"text": request.prompt})
    return {"word": request.prompt, "synonyms": response}


@app.get("/terms", response_class=HTMLResponse, tags=["Legal"])
async def terms_and_conditions(request: Request):
    return templates.TemplateResponse("terms.html", {"request": request})


@app.get("/privacy", response_class=HTMLResponse, tags=["Legal"])
async def privacy_policy(request: Request):
    return templates.TemplateResponse("privacy.html", {"request": request})


from fastapi.responses import RedirectResponse

@app.get("/terms-and-conditions", include_in_schema=False)
async def terms_redirect():
    return RedirectResponse(url="/terms", status_code=301)

@app.get("/privacy-policy", include_in_schema=False)
async def privacy_redirect():
    return RedirectResponse(url="/privacy", status_code=301)

app.mount("/static", StaticFiles(directory="static", check_dir=False), name="static")

handler = Mangum(app)