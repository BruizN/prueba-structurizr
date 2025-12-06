from fastapi import FastAPI, status, Depends, HTTPException
from sqlmodel import SQLModel, Field, create_engine
from contextlib import asynccontextmanager
from typing import Annotated

#Modelos
class GameBase(SQLModel):
    title: str = Field(index=True, min_length=3, max_length=30)
    platform: str = Field(min_length=2, max_length=15)
    hours_played: int = Field(gt=0, lt=100000)


class Game(GameBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


class GamePublic(GameBase):
    id: int

class GameUpdate():
    title: str | None = None
    platform: str | None = None
    hours_played: int | None = None 


#Conexion
POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "password" 
POSTGRES_DB = "games_db"
POSTGRES_HOST = "localhost"

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:5432/{POSTGRES_DB}"
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

SessionDep = Annotated[Session, Depends(get_session)]
app = FastAPI(lifespan=lifespan)

#Endpoints
@app.post("/games/", 
        response_model=status.HTTP_201_CREATED, 
        title="Registra un juego",
        response_model=GamePublic)
def create_game(game: GameBase, session: SessionDep):
    db_game = Game.model_validate(game)
    session.add(db_game)
    session.commit()
    session.refresh(db_game)
    return db_game


@app.get("/games/{game_id}/", title="Listar juegos registrados",
        response_model=list[GamePublic])
def read_games(game_id: int, session: SessionDep):
    game = session.get(Game, game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Juego no encontrado")
    return game


@app.get("/games/{game_id}/",
        title="Obtener un juego por su id",
        response_model=GamePublic)
def read_game(game_id: int, session: SessionDep):
    game = session.get(Game, game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Juego no encontrado")
    return game

@app.patch("/games/{game_id}/", 
        title="Actualizar un juego",
        response_model=GamePublic)
def update_game(game_id: int, game: GameUpdate, session: SessionDep):
    game_db = session