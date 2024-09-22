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


@app.post("/adducts/", response_model=list[pydantic_models.Adduct])
def create_adducts(
    adducts: list[pydantic_models.AdductCreate],
    db: Session = Depends(get_db)
    ):
    adducts_to_add = []
    for adduct in adducts:
        db_adduct_found = io.get_adduct_by_adduct_name(
            db, adduct_name=adduct.adduct_name
        )
        if not db_adduct_found:
            adducts_to_add.append(adduct)
                
    return io.create_adducts(db=db, adducts=adducts_to_add)


@app.get("/adducts/", response_model=list[pydantic_models.Adduct])
def get_adducts(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
    ):
    adducts = io.get_adducts(db, skip=skip, limit=limit)
    return adducts


@app.post(
    "/measured_compounds/",
    response_model=list[pydantic_models.MeasuredCompound]
)
def create_measured_compounds(
    measured_compounds: list[pydantic_models.MeasuredCompoundCreate],
    db: Session = Depends(get_db)
    ):
    msrd_cmps_to_add = []
    for msrd_cmp in measured_compounds:
        found = io.get_measured_compound_by_ids(
            db, 
            compound_id=msrd_cmp.compound_id,
            retention_time_id=msrd_cmp.retention_time_id,
            adduct_id=msrd_cmp.adduct_id
        )
        if not found:
            msrd_cmps_to_add.append(msrd_cmp)
        
    return io.create_measured_compound(db, msrd_cmps_to_add)


@app.get(
    "/measured_compounds/", 
    response_model=list[pydantic_models.MeasuredCompound]
)
def get_measured_compounds(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
    ):
    msrd_cmps = io.get_measured_compounds(db, skip=skip, limit=limit)
    return msrd_cmps


