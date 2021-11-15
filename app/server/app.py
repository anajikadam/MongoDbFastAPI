from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


from app.server.routes.student import router as StudentRouter

app = FastAPI()

app.include_router(StudentRouter, tags=["Student"], prefix="/student")


@app.get("/", tags=["Root"], response_class=HTMLResponse )
async def read_root(request: Request, ):
    templates = Jinja2Templates(directory="app/server/templates")
    return templates.TemplateResponse("index.html", {"request": request,})


##############################################################################
    # return """
    # <html>
    #     <head>
    #         <title>myFastAPI | Home</title>
    #     </head>
    #     <body>
    #         <h1>Welcome to the The Famous Peoples App | Web API </h1>
    #     </body>
    # </html>
    # """
    #return {"message": "Welcome to the The Famous Peoples App ......!!!!!"}

# uvicorn app.server.app:app --reload