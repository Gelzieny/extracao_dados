import uvicorn
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from routes.nasa_router import nasa_router
from routes.paises_router import paises_router

app = FastAPI(
  title="Extração de dados",
  description="",
  version="1.0.0"
)

app.include_router(paises_router)
app.include_router(nasa_router)

@app.get("/", include_in_schema=False)
def redirect_to_docs():
  return RedirectResponse(url="/docs")

if __name__ == "__main__":
  uvicorn.run(
    "main:app",
    port=8098,
    host="127.0.0.1",
    log_level="info",
    reload=True,
  )  