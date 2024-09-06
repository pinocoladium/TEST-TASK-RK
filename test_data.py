import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from models import Base, User

PG_USER = "admin"
PG_PASSWORD = "admin"
PG_HOST = "0.0.0.0"
PG_PORT = "5432"
PG_DB = "db"

PG_DSN = f"postgresql+psycopg2://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}"
conn = psycopg2.connect(
    user=PG_USER, database=PG_DB, password=PG_PASSWORD, host=PG_HOST, port=PG_PORT
)
engine = create_engine(PG_DSN)

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

with Session(bind=engine) as session:
    for el in range(10):
        t1 = User(
            username=f"user{el}",
            email=f"email{el}",
            password=f"rgvrggvbr{el}",
            points=6.7 + el,
            phone=f"454666777 {el}",
        )
        session.add_all([t1])
        session.commit()
