import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException

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