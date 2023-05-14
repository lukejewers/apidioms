from typing import Optional

from sqlmodel import Field, SQLModel


class Idiom(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    idiom: str
    part_of_speech: str
    link: str
