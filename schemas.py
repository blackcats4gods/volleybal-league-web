from pydantic import BaseModel
from typing import Optional, List

# Схема для создания команды (что присылает клиент)
class TeamCreate(BaseModel):
    name: str
    city: Optional[str] = None

# Схема для возврата команды из БД (что сервер отдает клиенту)
class TeamResponse(TeamCreate):
    id: int

    class Config:
        from_attributes = True

# Схема для создания игрока
class PlayerCreate(BaseModel):
    first_name: str
    last_name: str
    position: Optional[str] = None
    team_id: Optional[int] = None  # Привязка к id команды


# Схема для ответа игрока из БД
class PlayerResponse(PlayerCreate):
    id: int

    class Config:
        from_attributes = True

# Схема для создания матча (планирование игры)
class MatchCreate(BaseModel):
    home_team_id: int
    away_team_id: int


# Схема для внесения результата матча
class MatchResultUpdate(BaseModel):
    home_score: int
    away_score: int


# Схема ответа
class MatchResponse(MatchCreate):
    id: int
    home_score: int
    away_score: int
    is_completed: bool

    class Config:
        from_attributes = True

 # Схема для элемента турнирной таблицы
class StandingsRow(BaseModel):
    team_id: int
    team_name: str
    games_played: int
    wins: int
    losses: int
    points: int       