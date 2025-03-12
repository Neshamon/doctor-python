import requests as r
from typing import Annotated, Union
from pydantic import BaseModel
from pydantic_core import from_json
from fastapi import FastAPI, APIRouter, Request, Header, Form
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
brandList = r.get(f'{url}{apiOp}openfda.brand_name:{searchTerm}{limit}')
genericList = r.get(f'{url}{apiOp}openfda.generic_name:{searchTerm}{limit}')
manList = r.get(f'{url}{apiOp}openfda.manufacturer_name:{searchTerm}{limit}')
warnList = r.get(f'{url}{apiOp}boxed_warning:{searchTerm}{limit}')
dosageList = r.get(f'{url}{apiOp}dosage_and_administration:{searchTerm}{limit}')
useCaseList = r.get(f'{url}{apiOp}purpose{limit}')

doctor = FastAPI();

doctor.mount("/static", StaticFiles(directory="static/"), name="static")

@doctor.get("/")
async def root(request: Request):
    return templates.TemplateResponse("main.html", {"request": request})

@doctor.get("/brands/")
async def brands():
    return f"{brandList.text}"

@doctor.get("/search", response_class=HTMLResponse)
async def search(request: Request, query: str):
    rep = r.get(f'{url}{apiOp}openfda.brand_name:{query}{limit}')
    medObj = from_json(rep.text)
    medObj = medObj['results']
    results = [val for val in medObj]
    return templates.TemplateResponse(request=request, name="search.html", context= {"results": results})
