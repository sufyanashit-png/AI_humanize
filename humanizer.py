from fastapi import FastAPI
from pydantic import BaseModel
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os

# Load env variables
load_dotenv()

# Initialize FastAPI
app = FastAPI()

# Initialize Groq model
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.7
)

# Prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system",
     """You are an AI Humanizer.
     Your task is to rewrite any given text so it sounds natural,
     conversational, and written by a human. Avoid robotic tone.
     Keep the meaning the same but improve flow, readability,
     and human-like expression."""),
    
    ("human", "{text}")
])

parser = StrOutputParser()

# LangChain pipeline
chain = prompt | llm | parser


# Request model
class PromptRequest(BaseModel):
    prompt: str


# Humanize endpoint
@app.post("/humanize")
def humanize_text(request: PromptRequest):
    
    response = chain.invoke({
        "text": request.prompt
    })

    return {
        "original": request.prompt,
        "humanized": response
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)