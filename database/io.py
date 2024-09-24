from sqlalchemy.orm import Session

from . import pydantic_models, schema
import pandas as pd


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


def prepare_measured_compounds_create(
    db: Session, 
    measured_compounds: list[pydantic_models.MeasuredCompoundClient]
    ) -> dict:

    measured_compounds_create = []
    measured_compounds_invalid = []
    # Check compound_id and compound_name
    for mcc in measured_compounds:
        
        # Check compound
        compound = get_compound_by_id_name(
            db, mcc.compound_id, mcc.compound_name
        )
        if not compound:
            # raise ValueError(
            #     f"Compound with name {mcc.compound_name} and ID "
            #     f"{mcc.compound_id} does not exist in the database."
            # )
            measured_compounds_invalid.append(mcc)
            continue
        
        # Check adduct
        adduct = get_adduct_by_adduct_name(db, mcc.adduct_name)
        if not adduct:
            # raise ValueError(
            #     f"Adduct with name {mcc.adduct_name} does not exist in the "
            #     " database."
            # )
            measured_compounds_invalid.append(mcc)
            continue
        
        # Check or add retention_time
        rt = get_retention_time_by_value_comment(
            db, mcc.retention_time, mcc.retention_time_comment
        )
        if not rt:
            rt = create_retention_times(
                db, 
                [pydantic_models.RetentionTimeCreate(
                    retention_time=mcc.retention_time,
                    comment=mcc.retention_time_comment
                )]
            )[0]
            
        # Check molecular_formula
        
        
        
            
        # Create MeasuredCompoundCreate objects
        measured_compounds_create.append(
            pydantic_models.MeasuredCompoundCreate(
                compound_id=mcc.compound_id,
                retention_time_id=rt.retention_time_id,
                adduct_id=adduct.adduct_id
            )
        )
        
    if len(measured_compounds_create) == 0:
        raise ValueError("All input data is invalid. Please check it.")
    
    
    return {"valid": measured_compounds_create,
            "invalid": measured_compounds_invalid}

def create_measured_compounds(
    db: Session, 
    measured_compounds: list[pydantic_models.MeasuredCompoundCreate]
    ) -> list[schema.MeasuredCompound]:
    
    # Create db schema objects
    mc_schema = [
        schema.MeasuredCompound(
            compound_id=mc.compound_id,
            retention_time_id=mc.retention_time_id,
            adduct_id=mc.adduct_id
        )
        for mc in measured_compounds
        
        if not get_measured_compound_by_ids(
            db, mc.compound_id, mc.adduct_id, mc.retention_time_id
        )
    ]
    
    # Add to database
    db.add_all(mc_schema)
    db.commit()
    for mc in mc_schema:
        db.refresh(mc)
    
    return mc_schema


def get_measured_compounds(db: Session):
    result = (db.query(
                    schema.MeasuredCompound.compound_id,
                    schema.Compound.compound_name,
                    schema.RetentionTime.retention_time,
                    schema.RetentionTime.comment,
                    schema.Adduct.adduct_name,
                    schema.Compound.molecular_formula
                )
                .join(schema.RetentionTime, schema.MeasuredCompound.retention_time_id == schema.RetentionTime.retention_time_id)
                .join(schema.Compound, schema.MeasuredCompound.compound_id == schema.Compound.compound_id)
                .join(schema.Adduct, schema.MeasuredCompound.adduct_id == schema.Adduct.adduct_id)
                .all()
    )
    return result


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

def get_measured_compounds_by_rt_type_ion_mode(
    db: Session, 
    retention_time: float, 
    ion_mode: str,
    compound_type: str | None = None
):
    result = (db.query(
                    schema.MeasuredCompound.compound_id,
                    schema.Compound.compound_name,
                    schema.RetentionTime.retention_time,
                    schema.RetentionTime.comment,
                    schema.Adduct.adduct_name,
                    schema.Compound.molecular_formula
                )
                .join(schema.RetentionTime, schema.MeasuredCompound.retention_time_id == schema.RetentionTime.retention_time_id)
                .join(schema.Compound, schema.MeasuredCompound.compound_id == schema.Compound.compound_id)
                .join(schema.Adduct, schema.MeasuredCompound.adduct_id == schema.Adduct.adduct_id)
                .filter(
                    schema.RetentionTime.retention_time == retention_time,
                    schema.Compound.type == compound_type,
                    schema.Adduct.ion_mode == ion_mode
                )
                .all()
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