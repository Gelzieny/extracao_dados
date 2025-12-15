from fastapi import FastAPI, HTTPException
import requests
import uvicorn

from functions.all import agrupar_por_regiao

app = FastAPI(
  title="Extração de dados",
  description="",
  version="1.0.0"
)

REST_COUNTRIES_URL = "https://restcountries.com/v3.1/all?fields=name,population,region,flags"

def fetch_dados_paises():
  response = requests.get(REST_COUNTRIES_URL)
  if response.status_code == 200:
    return response.json()
  else:
    raise HTTPException(status_code=response.status_code, detail="Erro ao buscar dados dos países")

@app.get("/paises")
def get_paises():
  dados_paises = fetch_dados_paises()

  paises = []

  for pais in dados_paises:
    paises.append({
      "nome": pais["name"]["common"],
      "populacao": pais["population"],
      "regiao": pais["region"],
      "bandeira": pais.get("flags", {}).get("png")
    })

  resultado = agrupar_por_regiao(paises)
  return resultado


if __name__ == "__main__":
  uvicorn.run(
    "main:app",
    port=8098,
    host="127.0.0.1",
    log_level="info",
    reload=True,
  )  