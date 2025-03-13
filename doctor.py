import requests as r

from typing import Annotated, Union

from pydantic import BaseModel
from pydantic_core import from_json

from sqlmodel import Field, Session, SQLModel, create_engine, select

from fastapi import FastAPI, APIRouter, Request, Depends, Query, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory='templates/')
router = APIRouter()

url = 'https://api.fda.gov/drug/label.json'
searchTerm = "a*"
limit = "&limit=10"
apiOp = "?search="

doctor = FastAPI();

doctor.mount("/static", StaticFiles(directory="static/"), name="static")

class SearchHistory(SQLModel, table=True):
    brand_name: list
    generic_name: list
    manufacturer_name: list
    purpose: list
    warnings: list
    dosage_and_admin: list

doctorDb = create_engine("sqlite:///doctorDb.db", connect_args= {"check_same_thread": False})

def create_db_and_tables():
    SQLModel.metadata.create_all(doctorDb)

def get_session():
    with Session(doctorDb) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]
        
@doctor.get("/")
async def root(request: Request):
    return templates.TemplateResponse("main.html", {"request": request})

@doctor.get("/search", response_class=HTMLResponse)
async def search(request: Request, query: str):
    rep = r.get(f'{url}{apiOp}openfda.brand_name:{query}{limit}')
    medObj = from_json(rep.text)
    medObj = medObj['results']
    results = [val for val in medObj]
    
    return templates.TemplateResponse(request=request, name="search.html", context= {"results": results})

@doctor.get("/modal", response_class=HTMLResponse)
async def modal(request: Request, contentStr: str):
    return templates.TemplateResponse(request=request, name="modal.html", context={"contentStr": contentStr})
