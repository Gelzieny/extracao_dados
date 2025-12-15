from collections import defaultdict

def agrupar_por_regiao(paises: list[dict]) -> dict:
  agrupado = defaultdict(list)

  for pais in paises:
    regiao = pais.get("regiao", "Desconhecida")
    agrupado[regiao].append(pais)

  return dict(agrupado)