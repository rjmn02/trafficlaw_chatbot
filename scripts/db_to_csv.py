import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

# PC PATH
# FILE_PATH = "D:/Projects/trafficlaw-chatbot/data/processed/db_values.csv"

# LAPTOP PATH
FILE_PATH = os.getenv("DATA_PROCESSED_PATH", "")


def db_to_csv(outfile: str = FILE_PATH):
  db_url = os.getenv("DATABASE_URL")
  if not db_url:
    raise RuntimeError("DATABASE_URL env var not set")
  # Convert async URL (postgresql+asyncpg://) to sync (postgresql://)
  sync_url = db_url.replace("+asyncpg", "")
  engine = create_engine(sync_url)
  df = pd.read_sql("SELECT * FROM document", engine)
  df.to_csv(outfile, index=False)
  print(f"Wrote {len(df)} rows to {outfile}")


if __name__ == "__main__":
  db_to_csv()
