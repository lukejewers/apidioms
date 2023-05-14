import os
from typing import Generator

from sqlmodel import Session, SQLModel, create_engine, inspect

from .config import settings
from .models import Idiom

connect_args = {"check_same_thread": False}
engine = create_engine(settings.DATABASE_URI, echo=True, connect_args=connect_args)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


def SQLiteDBExists(filename):
    if not os.path.isfile(filename):
        return False
    return True


def create_db_and_tables():
    if inspect(engine).has_table("Idiom"):
        Idiom.__table__.drop(engine)
    SQLModel.metadata.create_all(engine)


def create_idioms():
    with open(settings.CSV_FILE_PATH, "r") as f:
        idioms = []
        for i, line in enumerate(f):
            if i == 0:
                continue

            if len(line.split(",")) == 3:
                idiom, pos, link = line.strip().split(",")
            else:
                try:
                    idiom, pos, link = list(filter(None, line.strip().split('"')))
                    pos = pos.strip(",")
                except ValueError:
                    idiom, pos, link = list(filter(None, line.strip().split("'")))

            idiom = Idiom(
                idiom=idiom,
                part_of_speech=pos,
                link=link,
            )
            idioms.append(idiom)

        session = next(get_session())
        session.bulk_save_objects(idioms)
        session.commit()
