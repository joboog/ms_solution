from sqlalchemy.orm import Session

import database.io as io
import database.schema as schema
import database.pydantic_models as pydantic_models
from database.database import SessionLocal, engine

schema.Base.metadata.create_all(bind=engine)

db = SessionLocal()

  
# # create test compounds objects
# test_compound = pydantic_models.CompoundCreate(
#   compound_id=6,
#   compound_name="test",
#   molecular_formula="C6H12O6",
#   type="sugar"
# )
# test_compound_2 = pydantic_models.CompoundCreate(
#   compound_name="test2",
#   molecular_formula="H2O",
#   type="water"
# )

# test_compound_3 = pydantic_models.CompoundCreate(
#   compound_name="test3",
#   molecular_formula="NaCl",
#   type="salt"
# )

# test_compound_4 = pydantic_models.CompoundCreate(
#   compound_name="test4",
#   molecular_formula="C2H5OH",
#   type="alcohol"
# )

# insert test compounds into database
# result = io.create_compound(db, compound=test_compound)
# result

# results2 = io.create_compounds(
#   db=db, compounds=[test_compound_2, test_compound_3, test_compound_4]
# )
# results2

# results = io.get_compounds_by_ids(db, [1])
# results

# mcc1 = pydantic_models.MeasuredCompoundClient(
#   compound_id=7,
#   compound_name="MCPA-D6",
#   retention_time=9.7,
#   adduct_name="M-H",
#   molecular_formula="C9H2[2]H6O3Cl1"
# )
# results = io.prepare_measured_compounds_create(db, [mcc1])
# results = io.create_measured_compounds(db, results)

def get_measured_compounds(db: Session):
    result = (db.query(
                    schema.MeasuredCompound.compound_id,
                    schema.Compound.compound_name,
                    schema.RetentionTime.retention_time,
                    schema.RetentionTime.comment,
                    schema.Adduct.adduct_name,
                    schema.MeasuredCompound.molecular_formula,
                    schema.MeasuredCompound.molecular_formula_c
                )
                .join(schema.RetentionTime, schema.MeasuredCompound.retention_time_id == schema.RetentionTime.retention_time_id)
                .join(schema.Compound, schema.MeasuredCompound.compound_id == schema.Compound.compound_id)
                .join(schema.Adduct, schema.MeasuredCompound.adduct_id == schema.Adduct.adduct_id)
                .all()
    )
    return result
  
list = get_measured_compounds(db)

import pandas as pd
df = pd.DataFrame(list, 
      columns=["compound_id", "compound_name", "retention_time", "comment", "adduct_name", "molecular_formula", "molecular_formula_c"]
)

any(df["molecular_formula_c"].isna())

from database.chem import parse_and_compute_mass

df["molecular_formula_c"].apply(parse_and_compute_mass)