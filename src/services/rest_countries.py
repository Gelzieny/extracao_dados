import requests

REST_COUNTRIES_URL = "https://restcountries.com/v3.1"

class RestCountriesService:
  def fetch_dados_paises(self):
    response = requests.get(f"{REST_COUNTRIES_URL}/all?fields=name,population,region,flags")
    if response.status_code == 200:
      return response.json()
    else:
      raise HTTPException(status_code=response.status_code, detail="Erro ao buscar dados dos países")

def fetch_pais_por_nome(self, nome: str):
  response = requests.get(f"{REST_COUNTRIES_URL}/name/{nome}", timeout=10)
  response.raise_for_status()
  return response.json()