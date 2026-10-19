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
     """You are a synonym generator.
        When given a single word, return a list of possible synonyms for that word.
        Only output the synonyms, separated by commas. Do not include explanations, sentences, or any additional text."""),
    
    ("human", "{text}")
])

parser = StrOutputParser()

# LangChain pipeline
chain = prompt | llm | parser


# Request model
class PromptRequest(BaseModel):
    prompt: str


@app.post("/synonyms")
def synonym_generator(request: PromptRequest):
    
    response = chain.invoke({
        "text": request.prompt
    })

    return {
        "word": request.prompt,
        "synonyms": response
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)