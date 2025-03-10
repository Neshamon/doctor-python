from fastapi import FastAPI
import requests as r

url = 'https://api.fda.gov/drug/label.json?'
medList = r.get(f'{url}search=openfda.brand_name:"a*"&limit=10')
useCaseList = r.get(f'{url}count=openfda&limit=1')


doctor = FastAPI();

@doctor.get("/")

async def root():
    return {"message": f"{medList.text}"}

async def brands():
    return f"{}"
