from pydantic import BaseModel


class CompoundBase(BaseModel):
    compound_name: str
    molecular_formula: str
    type: str | None = None

class CompoundCreate(CompoundBase):
    compound_id: int

class Compound(CompoundBase):
    compound_id: int
    #computed_mass: float

    class Config:
        orm_mode = True
        

class AdductBase(BaseModel):
    adduct_name: str
    mass_adjustment: float
    ion_mode: str

class AdductCreate(AdductBase):
    pass

class Adduct(AdductBase):
    adduct_id: int

    class Config:
        orm_mode = True
        

class MeasuredCompoundBase(BaseModel):
    compound_id: int
    retention_time_id: int
    adduct_id: int

class MeasuredCompoundCreate(MeasuredCompoundBase):
    pass

class MeasuredCompound(MeasuredCompoundBase):
    measured_compound_id: int

    class Config:
        orm_mode = True

class MeasuredCompoundClient(BaseModel):
    compound_id: int
    compound_name: str
    retention_time: float
    retention_time_comment: str | None = None
    adduct_name: str
    molecular_formula: str

class RetentionTimeBase(BaseModel):
    retention_time: float
    comment: str | None = None

class RetentionTimeCreate(RetentionTimeBase):
    pass

class RetentionTime(RetentionTimeBase):
    retention_time_id: int

    class Config:
        orm_mode = True