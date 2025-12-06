from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Field, Session, SQLModel, create_engine, select
from typing import Annotated
from contextlib import asynccontextmanager

class Games(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    platform: str
    hours_played: int = Field(gt=0)

#Conexion
POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "password" # Cambia esto por tu contraseña real
POSTGRES_DB = "games_db"
POSTGRES_HOST = "localhost"

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:5432/{POSTGRES_DB}"

# 3. CAMBIO AQUÍ: Engine limpio (sin check_same_thread)
engine = create_engine(DATABASE_URL, echo=True)

#Crecion de tablas
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

#Sesion
def get_session():
    with Session(engine) as session:
        yield session

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)

#Endpoints
@app.post("/games/", response_model=Games)
def create_game(game: Games, session: Session = Depends(get_session)):
    session.add(game)       
    session.commit()       
    session.refresh(game)   
    return game


@app.get("/games/", response_model=list[Games])
def read_games(session: Session = Depends(get_session)):
    games = session.exec(select(Games)).all()
    return games