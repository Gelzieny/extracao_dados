import uvicorn
import requests
from fastapi import APIRouter, Body, HTTPException, Depends

from functions.all import agrupar_por_regiao

parents_project = APIRouter(tags=["Parents Project"])


REST_COUNTRIES_URL = "https://restcountries.com/v3.1"

def fetch_dados_paises():
  response = requests.get(f"{REST_COUNTRIES_URL}/all?fields=name,population,region,flags")
  if response.status_code == 200:
    return response.json()
  else:
    raise HTTPException(status_code=response.status_code, detail="Erro ao buscar dados dos países")

@parents_project.get("/paises")
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

@parents_project.get("/pais/{nome}")
def bsucar_pais(nome:str):
  response = requests.get(f"{REST_COUNTRIES_URL}/name/{nome}")
  if response.status_code == 200:
    ret =  response.json()
    country = ret[0]
    capital = country.get("capital", [])

    return {
      "nome": country["name"]["common"],
      "populacao": country["population"],
      "regiao": country["region"],
      "subregiao": country.get("subregion", "Desconhecida"),
      "bandeira": country.get("flags", {}).get("png"),
      "capital": capital[0] if capital else None,
      "moeda": country.get("currencies", {}).get("XOF"),
      "idioma": country.get("languages", {}).get('fra')
    }

  else:
    raise HTTPException(status_code=response.status_code, detail="País não encontrado")

@parents_project.get("/pais/{nome}/moeda")
def bsucar_moeda(nome:str):
  response = requests.get(f"{REST_COUNTRIES_URL}/name/{nome}")
  if response.status_code == 200:
    ret =  response.json()
    country = ret[0]

    return {
      "nome": country["name"]["common"],
      "moeda": country["currencies"]
    }

  else:
    raise HTTPException(status_code=response.status_code, detail="País não encontrado")

@parents_project.get("/pais/{nome}/idioma")
def buscar_idioma(nome:str):
  response = requests.get(f"{REST_COUNTRIES_URL}/name/{nome}")
  if response.status_code == 200:
    ret =  response.json()


    country = ret[0]

    return {
      "nome": country["name"]["common"],
      "idioma": country.get("languages", {})
    }

  else:
    raise HTTPException(status_code=response.status_code, detail="País não encontrado")

@parents_project.get("/africa/independentes")
def buscar_indepentes_africa():
  response = requests.get(f"{REST_COUNTRIES_URL}/region/africa")
  if response.status_code == 200:
    paises_africa = response.json()

    independentes = [
      p["name"]["common"]
      for p in paises_africa
      if p.get("independent") is True
    ]

    return independentes
  else:
    raise HTTPException(status_code=response.status_code, detail="Erro ao buscar dados dos países")