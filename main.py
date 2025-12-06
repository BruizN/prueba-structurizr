from typing import Optional
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Field, Session, SQLModel, create_engine, select

# --- 1. EL MODELO (TABLA + ESQUEMA) ---
# Al heredar de SQLModel, esto es un modelo de Pydantic Y una tabla de SQLAlchemy a la vez.
class Hero(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)  # index=True hace que las busquedas por nombre sean rapidas
    secret_name: str
    age: Optional[int] = Field(default=None)

# --- 2. LA CONEXIÓN (ENGINE) ---
# Usamos SQLite. El archivo se llamará "database.db"
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

# connect_args es necesario solo para SQLite
engine = create_engine(sqlite_url, echo=True, connect_args={"check_same_thread": False})

# --- 3. CREACIÓN DE TABLAS ---
def create_db_and_tables():
    # Esto revisa los modelos y crea las tablas si no existen
    SQLModel.metadata.create_all(engine)

# --- 4. GESTIÓN DE SESIÓN (DEPENDENCY INJECTION) ---
# Esta función entrega una sesión de DB a cada petición y la cierra al terminar.
def get_session():
    with Session(engine) as session:
        yield session

# --- 5. LA APP FASTAPI ---
app = FastAPI()

# Evento que corre al iniciar la app
@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# --- 6. ENDPOINTS (Operaciones) ---

# Crear un Héroe
@app.post("/heroes/", response_model=Hero)
def create_hero(hero: Hero, session: Session = Depends(get_session)):
    session.add(hero)       # Agregamos a la sesión (memoria)
    session.commit()        # Guardamos en la DB
    session.refresh(hero)   # Actualizamos el objeto con el ID generado
    return hero

# Leer todos los Héroes
@app.get("/heroes/", response_model=list[Hero])
def read_heroes(session: Session = Depends(get_session)):
    heroes = session.exec(select(Hero)).all()
    return heroes