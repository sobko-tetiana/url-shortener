from fastapi import FastAPI

from src.routes import router

app = FastAPI()


app.include_router(router)


@app.get("/hello")
def read_root():
    return {"Hello": "World"}
