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

# 5. Создание (планирование) матча
@app.post("/api/v1/matches", response_model=schemas.MatchResponse)
def create_match(match: schemas.MatchCreate, db: Session = Depends(get_db)):
    if match.home_team_id == match.away_team_id:
        raise HTTPException(
            status_code=400,
            detail="Команда не может играть сама с собой",
        )

    new_match = models.Match(
        home_team_id=match.home_team_id, away_team_id=match.away_team_id
    )
    db.add(new_match)
    db.commit()
    db.refresh(new_match)
    return new_match


# 6. Внесение результата матча
@app.put(
    "/api/v1/matches/{match_id}/result", response_model=schemas.MatchResponse
)
def update_match_result(
    match_id: int,
    result: schemas.MatchResultUpdate,
    db: Session = Depends(get_db),
):
    match = (
        db.query(models.Match).filter(models.Match.id == match_id).first()
    )
    if not match:
        raise HTTPException(status_code=404, detail="Матч не найден")

    # Валидация волейбольного счета (кто-то должен выиграть 3 сета)
    if not (
        (result.home_score == 3 and result.away_score in [0, 1, 2])
        or (result.away_score == 3 and result.home_score in [0, 1, 2])
    ):
        raise HTTPException(
            status_code=400,
            detail="Некорректный волейбольный счет. Победитель должен взять ровно 3 сета",
        )

    match.home_score = result.home_score
    match.away_score = result.away_score
    match.is_completed = True

    db.commit()
    db.refresh(match)
    return match


# 7. Получение списка всех матчей
@app.get("/api/v1/matches", response_model=List[schemas.MatchResponse])
def get_matches(db: Session = Depends(get_db)):
    return db.query(models.Match).all()


# 8. Эндпоинт для получения турнирной таблицы
@app.get("/api/v1/standings", response_model=List[schemas.StandingsRow])
def get_standings(db: Session = Depends(get_db)):
    teams = db.query(models.Team).all()
    completed_matches = (
        db.query(models.Match).filter(models.Match.is_completed == True).all()
    )

    # Инициализируем статистику для каждой команды
    stats = {
        team.id: {
            "team_id": team.id,
            "team_name": team.name,
            "games_played": 0,
            "wins": 0,
            "losses": 0,
            "points": 0,
        }
        for team in teams
    }

    # Обсчитываем результаты всех завершенных матчей
    for match in completed_matches:
        home_id = match.home_team_id
        away_id = match.away_team_id

        # Пропускаем, если команда была удалена
        if home_id not in stats or away_id not in stats:
            continue

        stats[home_id]["games_played"] += 1
        stats[away_id]["games_played"] += 1

        # Победа хозяев
        if match.home_score == 3:
            stats[home_id]["wins"] += 1
            stats[away_id]["losses"] += 1

            if match.away_score in [0, 1]:
                stats[home_id]["points"] += 3
            elif match.away_score == 2:
                stats[home_id]["points"] += 2
                stats[away_id]["points"] += 1

        # Победа гостей
        elif match.away_score == 3:
            stats[away_id]["wins"] += 1
            stats[home_id]["losses"] += 1

            if match.home_score in [0, 1]:
                stats[away_id]["points"] += 3
            elif match.home_score == 2:
                stats[away_id]["points"] += 2
                stats[home_id]["points"] += 1

    # Превращаем словарь в список и сортируем по очкам (по убыванию)
    standings = list(stats.values())
    standings.sort(key=lambda x: x["points"], reverse=True)

    return standings