import os
from typing import Dict, List

from fastapi import Depends, FastAPI, HTTPException
from scraper.constants import parts_of_speech
from sqlmodel import Session, select

from .db import create_db_and_tables, create_idioms, get_session, SQLiteDBExists
from .models import Idiom

app = FastAPI()


@app.on_event("startup")
async def startup():
    filename = os.path.join("api", "idioms.db")
    if not SQLiteDBExists(filename):
        create_db_and_tables()
        create_idioms()


@app.post("/api/add-idiom/")
async def add_idiom(idiom: Dict[str, str], db: Session = Depends(get_session)):
    if not (candidate_idiom := idiom.get("idiom")):
        raise HTTPException(status_code=400, detail="Request body missing `idiom`")

    if not (pos := idiom.get("part_of_speech")):
        raise HTTPException(
            status_code=400,
            detail=f"Request body expects `part_of_speech` for `{candidate_idiom}`",
        )

    if pos not in parts_of_speech.dict().values():
        raise HTTPException(
            status_code=400,
            detail=f"Invalid `part_of_speech` for `{candidate_idiom}`",
        )

    if db.exec(select(Idiom).where(Idiom.idiom == idiom["idiom"])).first():
        raise HTTPException(
            status_code=400,
            detail=f"Idiom `{candidate_idiom}` already exists",
        )

    if idiom.get("link"):
        link = idiom["link"]
    else:
        link = "User Input"

    new_idiom = Idiom(idiom=candidate_idiom, part_of_speech=pos, link=link)
    db.add(new_idiom)
    db.commit()
    return f"Success! `{new_idiom.idiom}` added to db"


@app.get("/api/idioms", response_model=List[Idiom])
async def get_all_idioms(db: Session = Depends(get_session)):
    statement = select(Idiom)
    return db.exec(statement).all()


@app.get("/api/idiom/{idiom}")
async def get_idiom(idiom: str, db: Session = Depends(get_session)):
    statement = select(Idiom).where(Idiom.idiom == idiom)
    if not (result := db.exec(statement).first()):
        raise HTTPException(
            status_code=404, detail=f"No data for given idiom: `{idiom}`"
        )
    return result


@app.get("/api/random-idiom/")
async def get_random_idiom(db: Session = Depends(get_session)):
    statement = "SELECT * FROM Idiom ORDER BY RANDOM() LIMIT 1;"
    return db.exec(statement).first()


@app.get("/api/pos/{pos}")
async def get_pos(pos: str, db: Session = Depends(get_session)):
    statement = select(Idiom).where(Idiom.part_of_speech == pos)
    if not (result := db.exec(statement).all()):
        raise HTTPException(
            status_code=404, detail=f"Part of speech does not exist: `{pos}`"
        )
    return result


@app.patch("/api/update-idiom/")
async def update_idiom(idiom: Dict[str, str], db: Session = Depends(get_session)):
    if not (candidate_idiom := idiom.get("idiom")):
        raise HTTPException(
            status_code=400, detail=f"Valid idiom missing from request body"
        )

    if not idiom.get("part_of_speech") and not idiom.get("link"):
        raise HTTPException(status_code=400, detail=f"Request body missing patch data")

    statement = select(Idiom).where(Idiom.idiom == candidate_idiom)
    if not (db_idiom := db.exec(statement).first()):
        raise HTTPException(status_code=400, detail=f"Idiom `{idiom}` does not exist")

    for key, value in idiom.items():
        setattr(db_idiom, key, value)

    db.add(db_idiom)
    db.commit()
    db.refresh(db_idiom)
    return f"Success! {db_idiom.idiom} updated in db"


@app.delete("/api/delete-idiom/")
async def delete_idiom(idiom: str, db: Session = Depends(get_session)):
    statement = select(Idiom).where(Idiom.idiom == idiom)
    if not (result := db.exec(statement).first()):
        raise HTTPException(status_code=404, detail=f"Given idiom: `{idiom}` not in db")
    db.delete(result)
    db.commit()
    return f"Success! {result.idiom} deleted from db"
