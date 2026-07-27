from typing import List
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from database import Base, SessionLocal, engine
import models
import schemas

# Создаем таблицы в БД
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Volleyball League API")


# Зависимость для получения сессии БД на время запроса
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def read_root():
    return {"status": "ok", "message": "Volleyball League API is running"}


# 1. Эндпоинт для создания команды
@app.post("/api/v1/teams", response_model=schemas.TeamResponse)
def create_team(team: schemas.TeamCreate, db: Session = Depends(get_db)):
    # Проверяем, нет ли уже команды с таким именем
    db_team = (
        db.query(models.Team).filter(models.Team.name == team.name).first()
    )
    if db_team:
        raise HTTPException(
            status_code=400, detail="Команда с таким названием уже существует"
        )

    # Создаем новую запись в БД
    new_team = models.Team(name=team.name, city=team.city)
    db.add(new_team)
    db.commit()
    db.refresh(new_team)
    return new_team


# 2. Эндпоинт для получения всех команд
@app.get("/api/v1/teams", response_model=List[schemas.TeamResponse])
def get_teams(db: Session = Depends(get_db)):
    teams = db.query(models.Team).all()
    return teams

# 3. Эндпоинт для создания игрока
@app.post("/api/v1/players", response_model=schemas.PlayerResponse)
def create_player(player: schemas.PlayerCreate, db: Session = Depends(get_db)):
    # Если указан team_id, проверяем существование такой команды
    if player.team_id:
        team = (
            db.query(models.Team).filter(models.Team.id == player.team_id).first()
        )
        if not team:
            raise HTTPException(
                status_code=404, detail="Указанная команда не найдена"
            )

    new_player = models.Player(
        first_name=player.first_name,
        last_name=player.last_name,
        position=player.position,
        team_id=player.team_id,
    )
    db.add(new_player)
    db.commit()
    db.refresh(new_player)
    return new_player


# 4. Эндпоинт для получения всех игроков
@app.get("/api/v1/players", response_model=List[schemas.PlayerResponse])
def get_players(db: Session = Depends(get_db)):
    players = db.query(models.Player).all()
    return players