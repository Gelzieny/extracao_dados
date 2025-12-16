from fastapi import APIRouter
import requests

from functions.all import agrupar_por_regiao
from services.rest_countries import RestCountriesService

paises_router = APIRouter(prefix="/paises", tags=["Aula 01"])


@paises_router.get("/")
def get_paises():
  dados_paises = RestCountriesService().fetch_dados_paises()

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

@paises_router.get("/paises/{nome}")
def bsucar_pais(nome:str):
  response = RestCountriesService().fetch_pais_por_nome(nome)
  if response.status_code == 200:
    country = response[0]
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

@paises_router.get("/pais/{nome}/moeda")
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

@paises_router.get("/pais/{nome}/idioma")
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

@paises_router.get("/africa/independentes")
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
