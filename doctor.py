from fastapi import FastAPI

doctor = FastAPI();

@doctor.get("/")

async def root():
    return {"message": "Hello World"}
