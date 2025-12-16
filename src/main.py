from fastapi import FastAPI

from parents_project.parents_project import parents_project

app = FastAPI(
  title="Extração de dados",
  description="",
  version="1.0.0"
)


app.include_router(parents_project)

if __name__ == "__main__":
  uvicorn.run(
    "main:app",
    port=8098,
    host="127.0.0.1",
    log_level="info",
    reload=True,
  )  