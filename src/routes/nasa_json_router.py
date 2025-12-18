import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from requests.exceptions import Timeout, ConnectionError, RequestException

load_dotenv()

NASA_API_KEY = os.getenv("NASA_API_KEY")
NASA_APOD_URL = os.getenv("NASA_APOD_URL")

nasa_json_router = APIRouter(prefix="/apodjson", tags=["Aula 03"])


@nasa_json_router.get(
"/{date}",
summary="APOD por data e salvando em JSON",
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
    raise HTTPException(status_code=504, detail="Timeout da API da NASA")
  except ConnectionError:
    raise HTTPException(status_code=503, detail="Erro de conexão com a API da NASA")
  except RequestException:
    raise HTTPException(status_code=500, detail="Erro inesperado na requisição")

  if response.status_code != 200:
    raise HTTPException(
      status_code=response.status_code,
      detail="Erro ao acessar a API da NASA"
    )

  data = response.json()

  resultado = {
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

  os.makedirs("apod_json", exist_ok=True)

  file_path = f"apod_json/apod_{date}.json"
  with open(file_path, "w", encoding="utf-8") as f:
    json.dump(resultado, f, ensure_ascii=False, indent=2)

  return resultado
