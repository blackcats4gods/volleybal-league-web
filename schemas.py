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
