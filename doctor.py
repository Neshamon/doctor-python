from fastapi import FastAPI, APIRouter, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import requests as r

templates = Jinja2Templates(directory='./templates/')
router = APIRouter()

url = 'https://api.fda.gov/drug/label.json?'
brandList = r.get(f'{url}search=openfda.brand_name:"a*"&limit=10')
useCaseList = r.get(f'{url}count=openfda&limit=1')

doctor = FastAPI();

doctor.mount("/static", StaticFiles(directory="static/"), name="static")

@doctor.get("/")
async def root(request: Request):
    return templates.TemplateResponse("main.html", {"request": request})

@doctor.get("/brands/")
async def brands():
    return f"{brandList.text}"
