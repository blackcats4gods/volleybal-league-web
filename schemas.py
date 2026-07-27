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