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
    response_model=list[pydantic_models.MeasuredCompoundClient]
)
def create_measured_compounds(
    measured_compounds: list[pydantic_models.MeasuredCompoundClient],
    db: Session = Depends(get_db)
    ):
    try:
        msc_d = io.prepare_measured_compounds_create(db, measured_compounds)
        created = io.create_measured_compounds(db, msc_d["valid"])
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return msc_d["invalid"]

@app.get(
    "/measured_compounds/",
    response_model=list[pydantic_models.MeasuredCompoundClient]
)
def get_measured_compounds(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
    ):
    msrd_cmps = io.get_measured_compounds(db, skip=skip, limit=limit)
    return msrd_cmps

@app.get(
    "/measured_compounds/", 
    response_model=list[pydantic_models.MeasuredCompoundClient]
)
def get_measured_compounds_by_rt_type_ion_mode(
    retention_time: float,
    type: str,
    ion_mode: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
    ):
    msrd_cmps = io.get_measured_compounds_by_rt_type_ion_mode(
        db, retention_time, type, ion_mode, skip, limit
    )
    return msrd_cmps

@app.get(
    "/retention_times/", 
    response_model=list[pydantic_models.RetentionTime]
)
def get_retention_times(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
    ):
    rts = io.get_retention_times(db, skip=skip, limit=limit)
    return rts