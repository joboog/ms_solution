from sqlalchemy.orm import Session

from . import pydantic_models, schema
import pandas as pd


def create_compounds(db: Session, compounds: list[pydantic_models.CompoundCreate]):
    """
    Create and add multiple compounds to the database.
    Args:
        db (Session): SQLAlchemy database session.
        compounds (list[pydantic_models.CompoundCreate]): List of compounds to 
        be created.
    Returns:
        list[schema.Compound]: List of created compound objects.
    """
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
    """
    Retrieve a list of compounds from the database with optional pagination.
    """
    return db.query(schema.Compound).offset(skip).limit(limit).all()

def get_compound_by_compound_name(db: Session, compound_name: str):
    """
    Retrieve a compound from the database by its name.

    Args:
        db (Session): The database session to use for the query.
        compound_name (str): The name of the compound to retrieve.

    Returns:
        schema.Compound: The compound object if found, otherwise None.
    """
    result = (db.query(schema.Compound)
                .filter(schema.Compound.compound_name == compound_name)
                .first()
    )
    return result


def get_compound_by_id_name(
    db: Session,
    compound_id: int,
    compound_name: str
    ):
    """
    Retrieve compounds from the database by compound ID and name.

    Args:
        db (Session): The database session to use for the query.
        compound_id (int): The ID of the compound to retrieve.
        compound_name (str): The name of the compound to retrieve.

    Returns:
        List[schema.Compound]: A list of compounds matching the given ID and 
        name.
    """
    result = (db.query(schema.Compound)
                .filter(schema.Compound.compound_id == compound_id,
                        schema.Compound.compound_name == compound_name)
                .all()
    )
    return result


def create_adducts(db: Session, adducts: list[pydantic_models.AdductCreate]):
    """
    Creates and adds a list of adducts to the database.
    Args:
        db (Session): The database session to use for the operation.
        adducts (list[pydantic_models.AdductCreate]): A list of adducts to be 
        created and added to the database.
    Returns:
        list[schema.Adduct]: A list of the created adducts after being added 
        to the database.
    """
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
    """
    Retrieve a list of adducts from the database with pagination.

    Args:
        db (Session): The database session to use for the query.
        skip (int, optional): The number of records to skip. Defaults to 0.
        limit (int, optional): The maximum number of records to return. 
        Defaults to 100.

    Returns:
        List[schema.Adduct]: A list of adducts from the database.
    """
    return db.query(schema.Adduct).offset(skip).limit(limit).all()

def get_adduct_by_adduct_name(db: Session, adduct_name: str):
    """
    Retrieve an adduct from the database by its name.

    Args:
        db (Session): The database session to use for the query.
        adduct_name (str): The name of the adduct to retrieve.

    Returns:
        schema.Adduct: The adduct object if found, otherwise None.
    """
    result = (db.query(schema.Adduct)
                .filter(schema.Adduct.adduct_name == adduct_name)
                .first()
    )
    return result


def prepare_measured_compounds_create(
    db: Session, 
    measured_compounds: list[pydantic_models.MeasuredCompoundClient]
    ) -> dict:
    """
    Prepares a list of MeasuredCompoundCreate objects for creation in the 
    database. This function validates the provided measured compounds by 
    checking the existence of the compound, adduct, and retention time in the
    database. If any of these entities do not exist, the corresponding measured
    compound is marked as invalid. 
    Otherwise, it prepares the MeasuredCompoundCreate objects for valid entries.
    Args:
        db (Session): The database session.
        measured_compounds (list[pydantic_models.MeasuredCompoundClient]): 
            A list of MeasuredCompoundClient objects to be validated and 
            prepared.
    Returns:
        dict: A dictionary with two keys:
            - "valid": A list of MeasuredCompoundCreate objects that are valid 
            and  ready for creation.
            - "invalid": A list of MeasuredCompoundClient objects that are 
            invalid due to missing compound, adduct, or retention time.
    Raises:
        ValueError: If all input data is invalid.
    """
    
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
    """
    Create and store measured compounds in the database.
    This function takes a list of measured compounds, checks if they already 
    exist in the database,
    and if not, creates new entries for them.
    Args:
        db (Session): The database session to use for the operation.
        measured_compounds (list[pydantic_models.MeasuredCompoundCreate]): A 
        list of measured compound creation models containing the necessary data
        to create new measured compounds.
    Returns:
        list[schema.MeasuredCompound]: A list of the created measured compound schema objects.
    """
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
    
    db.add_all(mc_schema)
    db.commit()
    for mc in mc_schema:
        db.refresh(mc)
    
    return mc_schema


def get_measured_compounds(db: Session):
    """
    Retrieve measured compounds from the database.

    This function queries the database to retrieve information about measured 
    compounds, including their compound ID, compound name, retention time, 
    comments, and adduct name.

    Args:
        db (Session): SQLAlchemy session object for database interaction.

    Returns:
        List[Tuple[int, str, float, str, str]]: A list of tuples containing 
        the following information:
            - compound_id (int): The ID of the compound.
            - compound_name (str): The name of the compound.
            - retention_time (float): The retention time of the compound.
            - comment (str): Any comments associated with the retention time.
            - adduct_name (str): The name of the adduct.
    """
    result = (db.query(
                    schema.MeasuredCompound.compound_id,
                    schema.Compound.compound_name,
                    schema.RetentionTime.retention_time,
                    schema.RetentionTime.comment,
                    schema.Adduct.adduct_name
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
    """
    Retrieve a measured compound from the database by its compound ID, adduct 
    ID, and retention time ID.

    Args:
        db (Session): The database session to use for the query.
        compound_id (int): The ID of the compound.
        adduct_id (int): The ID of the adduct.
        retention_time_id (int): The ID of the retention time.

    Returns:
        MeasuredCompound: The measured compound that matches the given IDs, or 
        None if no match is found.
    """
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
    """
    Retrieve measured compounds from the database based on retention time, ion 
    mode, and optional compound type.

    Args:
        db (Session): The database session to use for the query.
        retention_time (float): The retention time to filter compounds.
        ion_mode (str): The ion mode to filter compounds.
        compound_type (str | None, optional): The type of compound to filter. 
        Defaults to None.

    Returns:
        list: A list of tuples containing the compound ID, compound name, 
        retention time, comment, adduct name, and molecular formula.
    """
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
    """
    Creates and stores retention times in the database.
    Args:
        db (Session): The database session to use for the operation.
        retention_times (list[pydantic_models.RetentionTimeCreate]): A list of 
        retention time objects to be created.
    Returns:
        list[schema.RetentionTime]: A list of the created retention time 
        objects with refreshed state from the database.
    """
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
    """
    Retrieve retention times from the database with optional pagination.

    Args:
        db (Session): The database session to use for the query.
        skip (int, optional): The number of records to skip. Defaults to 0.
        limit (int, optional): The maximum number of records to return. 
        Defaults to 100.

    Returns:
        List[RetentionTime]: A list of retention time records.
    """
    return db.query(schema.RetentionTime).offset(skip).limit(limit).all()

def get_retention_time_by_value_comment(
    db: Session, 
    retention_time: float,
    comment: str
    ):
    """
    Retrieve a retention time record from the database based on the retention 
    time value and comment.

    Args:
        db (Session): The database session to use for the query.
        retention_time (float): The retention time value to filter by.
        comment (str): The comment to filter by.

    Returns:
        schema.RetentionTime: The first retention time record that matches 
        the given retention time and comment, or None if no match is found.
    """
    result = (db.query(schema.RetentionTime)
                .filter(schema.RetentionTime.retention_time == retention_time,
                        schema.RetentionTime.comment == comment
                )
                .first()
    )
    return result