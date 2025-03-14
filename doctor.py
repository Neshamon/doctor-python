from ntpath import exists
import requests as r

from typing import Annotated

from pydantic_core import from_json

from sqlmodel import Field, Session, SQLModel, create_engine, select

from contextlib import asynccontextmanager

from fastapi import FastAPI, APIRouter, Request, Depends, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory='templates/')
router = APIRouter()

url = 'https://api.fda.gov/drug/label.json'
limit = "&limit=10"
apiOp = "?search="

class SearchHistory(SQLModel, table=True):
    id: int | None = Field(None, primary_key=True, index=True)
    brand_name: str | None = Field(None, index=True)
    generic_name: str = Field(None, index=True)
    manufacturer_name: str = Field(None, index=True)
    purpose: str = Field(None, index=True)
    warnings: str = Field(None, index=True)
    dosage_and_admin: str = Field(None, index=True)

doctorDb = create_engine("sqlite:///./doctor.db", connect_args= {"check_same_thread": False})

def create_db_and_tables():
    SQLModel.metadata.create_all(doctorDb)

def get_session():
    with Session(doctorDb) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

@asynccontextmanager
async def lifespan(app: FastAPI):
    if not exists("./doctor.db"):
        create_db_and_tables()
    yield

doctor = FastAPI(lifespan=lifespan);

doctor.mount("/static", StaticFiles(directory="static/"), name="static")

@doctor.get("/")
async def root(request: Request):
    return templates.TemplateResponse("main.html", {"request": request})

@doctor.post("/cache")
async def cache(doc: SearchHistory, session: SessionDep):
    session.add(doc)
    session.commit()
    session.refresh(doc)
    print("\nResponse Cached!\n")
    return doc

@doctor.get("/history")
async def get_history(searchStr: str, session: SessionDep):
    statement = select(SearchHistory).where(SearchHistory.brand_name == searchStr)
    query = session.exec(statement)
    queryResults = query.all()
    if not query:
        print("\nQuery not found.\n")
        return False
    return queryResults
    
@doctor.get("/search", response_class=HTMLResponse)
async def search(request: Request, query: str):
    results = ''
    history = ''
    if query == '':
        return
    else:
        with Session(doctorDb) as session:     
            history = await get_history(query, session)

    if not history:
        rep = r.get(f'{url}{apiOp}openfda.brand_name:{query}{limit}')
        medObj = from_json(rep.text)
        medObj = medObj['results']
        results = [val for val in medObj]
        searchList = []
        for dataObj in results:
            searchList.append(SearchHistory(
                brand_name=dataObj['openfda']['brand_name'][0] if dataObj.get('openfda') else 'No Data',
                generic_name=dataObj['openfda']['generic_name'][0] if dataObj.get('openfda') else 'No Data',
                manufacturer_name=dataObj['openfda']['manufacturer_name'][0] if dataObj.get('openfda') else 'No Data',
                purpose=dataObj['purpose'][0] if dataObj.get('purpose') else 'No Data',
                warnings=dataObj['warnings'][0] if dataObj.get('warnings') else 'No Data',
                dosage_and_admin=dataObj['dosage_and_administration'][0] if dataObj.get('dosage_and_administration') else 'No Data'
            ))
        
        with Session(doctorDb) as session:
            [await cache(item, session) for item in searchList]
    else:
        #[print(item, "\n\n\n\n\n") for item in history]
        results = history

    return templates.TemplateResponse(request=request, name="search.html", context= {"results": results})
    

@doctor.get("/modal", response_class=HTMLResponse)
async def modal(request: Request, contentStr: str):
    return templates.TemplateResponse(request=request, name="modal.html", context={"contentStr": contentStr})

@doctor.delete("/modal", response_class=HTMLResponse)
async def close_modal(request: Request):
    return templates.TemplateResponse(request=request, name="empty.html", context={'request': request})

@doctor.get("/api/drugs", response_class=JSONResponse)
async def drugs(query: str):
    history = ''
    with Session(doctorDb) as session:
        history = await get_history(query, session)

    if not history:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content="No data")
    else:
        result = jsonable_encoder(history)
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)
