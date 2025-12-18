import io
import os
import re
import unicodedata
import pandas as pd
from datetime import datetime
from fastapi.responses import FileResponse
from fastapi import APIRouter, UploadFile, File, HTTPException

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "csv_tratados")
os.makedirs(OUTPUT_DIR, exist_ok=True)

imdb_router = APIRouter(prefix="/imdb_file", tags=["Aula 03"])

def fix_mojibake(text: str) -> str:
  """
  Corrige texto UTF-8 lido como latin1 (acentos quebrados).
  Ex: 'titlÃª' -> 'title'
  """
  try:
    return text.encode("latin1").decode("utf-8")
  except Exception:
    return text

def normalize_text(text):
  if pd.isna(text):
    return "N/A"

  text = str(text)

  text = fix_mojibake(text)

  text = unicodedata.normalize("NFKC", text)

  text = re.sub(r"[\x00-\x1f\x7f]", "", text)
  text = text.replace("�", "").strip()

  return text if text else "N/A"

def format_brl(valor):
  if pd.isna(valor) or valor == 0:
    return "N/A"

  return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def format_date(valor):
  try:
    data = pd.to_datetime(valor, dayfirst=True, errors="coerce")
    if pd.isna(data):
      return "N/A"
    return data.strftime("%d/%m/%Y")
  except Exception:
      return "N/A"
      
def perform_cleanup(df: pd.DataFrame) -> pd.DataFrame:
  df = df.copy()

  df.columns = [fix_mojibake(col) for col in df.columns]

  df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
  )

  df.rename(columns={
    "imbd_title_id": "imdb_title_id",
    "original_titlê": "original_title",
    "original_titlãª": "original_title",
    "genrë¨": "genre",
    "genrã«â¨": "genre"
  }, inplace=True)

  df = df.loc[:, ~df.columns.str.startswith("unnamed")]

  df.dropna(how="all", inplace=True)

  invalid_values = ["", " ", "null", "nan", "inf", "-", "not applicable", "#n/a"]
  df.replace(invalid_values, pd.NA, inplace=True)

  if "duration" in df.columns:
    df["duration"] = df["duration"].astype(str).str.extract(r"(\d+)")
    df["duration"] = pd.to_numeric(df["duration"], errors="coerce")

  if "score" in df.columns:
    df["score"] = (
      df["score"]
      .astype(str)
      .str.replace(",", ".", regex=False)
      .str.extract(r"(\d+\.?\d*)")
    )
    df["score"] = pd.to_numeric(df["score"], errors="coerce")

  if "votes" in df.columns:
    df["votes"] = df["votes"].astype(str).str.replace(".", "", regex=False)
    df["votes"] = pd.to_numeric(df["votes"], errors="coerce")

  if "income" in df.columns:
    df["income"] = df["income"].astype(str).str.replace(r"[^\d]", "", regex=True)
    df["income"] = pd.to_numeric(df["income"], errors="coerce")

  if "release_year" in df.columns:
    df["release_year"] = df["release_year"].apply(format_date)

  for col in ["original_title", "genre", "country", "director", "content_rating"]:
    if col in df.columns:
      df[col] = df[col].apply(normalize_text)

  if "income" in df.columns:
    df["income"] = df["income"].apply(format_brl)

  df = df.fillna("N/A")

  rename_map = {
    "imdb_title_id": "id_imdb",
    "original_title": "titulo_original",
    "release_year": "ano_lancamento",
    "genre": "genero",
    "duration": "duracao",
    "country": "pais",
    "content_rating": "classificacao_indicativa",
    "director": "diretor",
    "income": "receita",
    "votes": "votos",
    "score": "nota"
  }

  df.rename(columns=rename_map, inplace=True)

  return df

@imdb_router.post("/upload-save-download")
async def upload_save_and_download_csv(file: UploadFile = File(...)):
  if not file.filename.lower().endswith(".csv"):
    raise HTTPException(status_code=400, detail="Envie um arquivo CSV válido.")

  contents = await file.read()

  df = pd.read_csv(
    io.BytesIO(contents),
    sep=";",
    encoding="latin1"
  )

  df_cleaned = perform_cleanup(df)

  timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
  filename = f"imdb_tratado_{timestamp}.csv"
  file_path = os.path.join(OUTPUT_DIR, filename)

  df_cleaned.to_csv(
    file_path,
    sep=";",
    index=False,
    encoding="utf-8-sig",
    lineterminator="\n"
  )

  return FileResponse(path=file_path, filename=filename, media_type="text/csv")
