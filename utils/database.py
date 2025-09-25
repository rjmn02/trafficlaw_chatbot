import psycopg2
from psycopg2.extras import Json

def get_db():
  return psycopg2.connect(
    dbname="trafficlaw",
    user="postgres",
    password="yourpassword",
    host="localhost",
    port=5432
  )
  