from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.routes import router

app = FastAPI()

app.mount("/static", StaticFiles(directory="src/static"), name="static")


# These page routes are registered before `router` (which has a
# single-segment catch-all, GET /{shortened_url_code}) on purpose: Starlette
# matches routes in registration order, so an exact route like "/login" must
# come first or the shortener would swallow it as a lookup for a short code
# literally named "login".
@app.get("/")
async def index():
    return FileResponse("src/static/index.html")


@app.get("/login")
async def login_page():
    return FileResponse("src/static/login.html")


@app.get("/register")
async def register_page():
    return FileResponse("src/static/register.html")


@app.get("/links")
async def urls_page():
    return FileResponse("src/static/urls.html")


app.include_router(router)


@app.get("/hello")
def read_root():
    return {"Hello": "World"}


@app.exception_handler(StarletteHTTPException)
async def not_found_page(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404 and "text/html" in request.headers.get("accept", ""):
        return FileResponse("src/static/404.html", status_code=404)
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
