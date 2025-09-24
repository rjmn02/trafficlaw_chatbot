import pandas as pd
import psycopg2


def db_to_csv():
  db_con = psycopg2.connect(
    database="trafficlawdb", 
    user="root", 
    password="rootpass",
    host="localhost",
    port = "5432",
  )

  df = pd.read_sql_query("SELECT * FROM langchain_pg_embedding", db_con)
  df.to_csv("db_values.csv", index=False)
  db_con.close()
  
if __name__ == "__main__":
  db_to_csv()