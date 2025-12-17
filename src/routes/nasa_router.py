import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from requests.exceptions import Timeout, ConnectionError, RequestException


load_dotenv()

NASA_API_KEY = os.getenv("NASA_API_KEY")
NASA_APOD_URL = os.getenv("NASA_APOD_URL")

nasa_router = APIRouter(prefix="/apod", tags=["Aula 02"])

@nasa_router.get(
  "",
  summary="Astronomy Picture of the Day",
  description="""
Retorna a **Imagem Astronômica do Dia (APOD)** fornecida pela NASA.

Os dados retornados incluem:
- **Título**
- **Data formatada (DD/MM/YYYY)**
- **Tipo de mídia** (imagem ou vídeo)
- **URL da imagem**
- **URL da imagem em alta resolução**
- **Descrição científica**
- **Créditos do autor (quando disponíveis)**

A imagem muda **uma vez por dia**.
"""
)
def get_apod():
  response = requests.get(NASA_APOD_URL, params={"api_key": NASA_API_KEY})

  if response.status_code != 200:
    raise HTTPException(status_code=500, detail="Erro ao acessar APOD")

  data = response.json()
  date_str = data["date"]

  treated_data = {
    "title": data.get("title"),
    "date": datetime.strptime(date_str, "%Y-%m-%d").strftime("%d/%m/%Y"),
    "media_type": data.get("media_type"),
    "image_url": data.get("url"),
    "hd_image_url": data.get("hdurl"),
    "description": data.get("explanation"),
    "copyright": (
      data.get("copyright", "").strip()
      if data.get("copyright") else None
    )
  }

  return treated_data

@nasa_router.get(
  "/{date}",
  summary="APOD por data",
  description="""
Retorna a **Astronomy Picture of the Day (APOD)** da NASA para uma data específica.

Formato da data:
- `YYYY-MM-DD` (ex: `2025-12-16`)
"""
)
def get_apod_by_date(date: str):

  try:
    datetime.strptime(date, "%Y-%m-%d")
  except ValueError:
    raise HTTPException(
      status_code=400,
      detail="Formato de data inválido. Use YYYY-MM-DD (ex: 1991-06-01)"
    )

  try:
    response = requests.get(
      NASA_APOD_URL,
      params={
        "api_key": NASA_API_KEY,
        "date": date
      },
      timeout=10
    )

  except Timeout:
    raise HTTPException(
      status_code=504,
      detail="Tempo de resposta da API da NASA excedido (timeout)"
    )

  except ConnectionError:
    raise HTTPException(
      status_code=503,
      detail="Erro de conexão com a API da NASA"
    )

  except RequestException:
    raise HTTPException(
      status_code=500,
      detail="Erro inesperado ao realizar a requisição"
    )

  if response.status_code == 200:
    data = response.json()

  elif response.status_code == 401:
    raise HTTPException(
      status_code=401,
      detail="Chave da API inválida ou não autorizada"
    )

  elif response.status_code == 429:
    raise HTTPException(
      status_code=429,
      detail="Limite de requisições da API da NASA excedido"
    )

  else:
    raise HTTPException(
      status_code=response.status_code,
      detail="Erro inesperado ao acessar a API da NASA"
    )

  return {
    "title": data.get("title"),
    "date": datetime.strptime(
      data["date"], "%Y-%m-%d"
    ).strftime("%d/%m/%Y"),
    "media_type": data.get("media_type"),
    "image_url": data.get("url"),
    "hd_image_url": data.get("hdurl"),
    "description": data.get("explanation"),
    "copyright": (
      data.get("copyright", "").strip()
      if data.get("copyright") else None
    )
  }