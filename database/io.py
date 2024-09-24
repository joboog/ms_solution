from sqlalchemy.orm import Session

from . import pydantic_models, schema


def create_compound(db: Session, compound: pydantic_models.CompoundCreate):
    db_compound = schema.Compound(
        compound_id=compound.compound_id,
        compound_name=compound.compound_name, 
        molecular_formula=compound.molecular_formula,
        type=compound.type
    )
    db.add(db_compound)
    db.commit()
    db.refresh(db_compound)
    return db_compound


def create_compounds(db: Session, compounds: list[pydantic_models.CompoundCreate]):
    db_compounds = [
        schema.Compound(
            compound_id=compound.compound_id,
            compound_name=compound.compound_name,
            molecular_formula=compound.molecular_formula,
            type=compound.type
        )
        for compound in compounds
    ]
    db.add_all(db_compounds)
    db.commit()
    for compound in db_compounds:
        db.refresh(compound)
    
    return db_compounds


def get_compounds(db: Session, skip: int = 0, limit: int = 100):
    return db.query(schema.Compound).offset(skip).limit(limit).all()

def get_compound_by_compound_name(db: Session, compound_name: str):
    result = (db.query(schema.Compound)
                .filter(schema.Compound.compound_name == compound_name)
                .first()
    )
    return result

def get_compounds_by_ids(db: Session, compound_ids: list[int]):
    result = (db.query(schema.Compound)
                .filter(schema.Compound.compound_id.in_(compound_ids))
                .all()
    )
    return result

def get_compound_by_id_name(
    db: Session,
    compound_id: int,
    compound_name: str):
    result = (db.query(schema.Compound)
                .filter(schema.Compound.compound_id == compound_id,
                        schema.Compound.compound_name == compound_name)
                .all()
    )
    return result


def create_adducts(db: Session, adducts: list[pydantic_models.AdductCreate]):
    db_adducts = [
        schema.Adduct(
            adduct_name=adduct.adduct_name,
            mass_adjustment=adduct.mass_adjustment,
            ion_mode=adduct.ion_mode
        )
        for adduct in adducts
    ]
    db.add_all(db_adducts)
    db.commit()
    for adduct in db_adducts:
        db.refresh(adduct)
    
    return db_adducts

def get_adducts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(schema.Adduct).offset(skip).limit(limit).all()

def get_adduct_by_adduct_name(db: Session, adduct_name: str):
    result = (db.query(schema.Adduct)
                .filter(schema.Adduct.adduct_name == adduct_name)
                .first()
    )
    return result


def create_measured_compounds(
    db: Session, 
    measured_compounds: list[pydantic_models.MeasuredCompoundCreate]
    ):
    db_measured_compounds = [
        schema.MeasuredCompound(
            compound_id=measured_compound.compound_id,
            retention_time_id=measured_compound.retention_time_id,
            adduct_id=measured_compound.adduct_id
        )
        for measured_compound in measured_compounds
    ]
    db.add_all(db_measured_compounds)
    db.commit()
    for measured_compound in db_measured_compounds:
        db.refresh(measured_compound)
    
    return db_measured_compounds


def get_measured_compounds(db: Session, skip: int = 0, limit: int = 100):
    return db.query(schema.MeasuredCompound).offset(skip).limit(limit).all()


def get_measured_compound_by_ids(
    db: Session, 
    compound_id: int,
    adduct_id: int,
    retention_time_id: int
    ):
    result = (db.query(schema.MeasuredCompound)
                .filter(
                    schema.MeasuredCompound.compound_id == compound_id,
                    schema.MeasuredCompound.adduct_id == adduct_id,
                    schema.MeasuredCompound.retention_time_id == retention_time_id
                )
                .first()
    )
    return result


def create_retention_times(
    db: Session, 
    retention_times: list[pydantic_models.RetentionTimeCreate]
    ):
    db_rts = [
        schema.RetentionTime(
            retention_time=rt.retention_time,
            comment=rt.comment
        )
        for rt in retention_times
    ]
    db.add_all(db_rts)
    db.commit()
    for rt in db_rts:
        db.refresh(rt)
    
    return db_rts

def get_retention_times(db: Session, skip: int = 0, limit: int = 100):
    return db.query(schema.RetentionTime).offset(skip).limit(limit).all()

def get_retention_time_by_value_comment(
    db: Session, 
    retention_time: float,
    comment: str
    ):
    result = (db.query(schema.RetentionTime)
                .filter(schema.RetentionTime.retention_time == retention_time,
                        schema.RetentionTime.comment == comment
                )
                .first()
    )
    return result


def get_retention_time_by_value(
    db: Session, 
    retention_time: float
    ):
    result = (db.query(schema.RetentionTime)
                .filter(schema.RetentionTime.retention_time == retention_time)
                .first()
    )
    return result