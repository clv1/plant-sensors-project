from os import environ
from dotenv import load_dotenv
from sqlalchemy import create_engine, sql


if __name__ == "__main__":
    load_dotenv()
    engine = create_engine(
        f"mssql+pymssql://{environ['DB_USER']}:{environ['DB_PASSWORD']}@{environ['DB_HOST']}/?charset=utf8")
    conn = engine.connect()
    conn.execute(sql.text("USE plants;"))
    query = sql.text("INSERT INTO s_alpha.example (msg) VALUES (:msg)")
    conn.execute(query, {"msg": "horse"})
    query = sql.text("SELECT * FROM s_alpha.example;")
    conn.execute(sql.text("COMMIT;"))
    res = conn.execute(query).fetchall()
    print(res)
