from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import io, pydantic_models, schema
from .database import SessionLocal, engine

schema.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/compound/", response_model=pydantic_models.Compound)
def create_compound(
  compound: pydantic_models.CompoundCreate,
  db: Session = Depends(get_db)
  ):
    db_compund = io.get_compound_by_compound_name(
      db, compound_name=compound.compound_name
    )
    if db_compund:
        raise HTTPException(status_code=400, detail="Compound already exists")
    return io.create_compound(db=db, compound=compound)

@app.post("/compounds/", response_model=list[pydantic_models.Compound])
def create_compounds(
    compounds: list[pydantic_models.CompoundCreate],
    db: Session = Depends(get_db)
    ):
    compounds_to_add = []
    for compound in compounds:
        db_compound_found = io.get_compound_by_compound_name(
            db, compound_name=compound.compound_name
        )
        if not db_compound_found:
            compounds_to_add.append(compound)
                
    return io.create_compounds(db=db, compounds=compounds_to_add)


@app.get("/compounds/", response_model=list[pydantic_models.Compound])
def get_compounds(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
    ):
    compounds = io.get_compounds(db, skip=skip, limit=limit)
    return compounds
