from pydantic import BaseModel


class CompoundBase(BaseModel):
    """
    CompoundBase is a Pydantic model representing the basic information of a 
    chemical compound.

    Attributes:
        compound_name (str): The name of the compound.
        molecular_formula (str): The molecular formula of the compound.
        type (Optional[str]): The type of the compound, which can be None.
    """
    compound_name: str
    molecular_formula: str
    type: str | None = None

class CompoundCreate(CompoundBase):
    """
    CompoundCreate is a Pydantic model that inherits from CompoundBase.
    It represents the creation schema for a compound with the following 
    attribute:

    Attributes:
        compound_id (int): The unique identifier for the compound.
    """
    compound_id: int

class Compound(CompoundBase):
    """
    Represents a compound with an ID and computed mass.

    Attributes:
        compound_id (int): The unique identifier for the compound.
        computed_mass (float): The computed mass of the compound.

    Config:
        orm_mode (bool): Enables ORM mode for compatibility with ORMs like
        SQLAlchemy.
    """
    compound_id: int
    computed_mass: float

    class Config:
        orm_mode = True
        

class AdductBase(BaseModel):
    """
    AdductBase is a Pydantic model representing an adduct with its associated 
    properties.

    Attributes:
        adduct_name (str): The name of the adduct.
        mass_adjustment (float): The mass adjustment value for the adduct.
        ion_mode (str): The ion mode associated with the adduct.
    """
    adduct_name: str
    mass_adjustment: float
    ion_mode: str

class AdductCreate(AdductBase):
    """
    AdductCreate is a Pydantic model that inherits from AdductBase.
    This class is used for creating new Adduct records.
    """
    pass

class Adduct(AdductBase):
    """
    Adduct model that extends AdductBase with an additional adduct_id field.

    Attributes:
        adduct_id (int): Unique identifier for the adduct.

    Config:
        orm_mode (bool): Enables ORM mode for compatibility with ORMs like 
        SQLAlchemy.
    """
    adduct_id: int

    class Config:
        orm_mode = True
        

class MeasuredCompoundBase(BaseModel):
    """
    MeasuredCompoundBase is a Pydantic model representing the base structure 
    for a measured compound.

    Attributes:
        compound_id (int): The unique identifier for the compound.
        retention_time_id (int): The identifier for the retention time 
        associated with the compound.
        adduct_id (int): The identifier for the adduct associated with the 
        compound.
    """
    compound_id: int
    retention_time_id: int
    adduct_id: int

class MeasuredCompoundCreate(MeasuredCompoundBase):
    """
    MeasuredCompoundCreate is a Pydantic model that inherits from 
    MeasuredCompoundBase.
    This class is used for creating new instances of measured compounds.
    Currently, it does not add any additional fields or methods to the base class.
    """
    pass

class MeasuredCompound(MeasuredCompoundBase):
    """
    MeasuredCompound model extending MeasuredCompoundBase.

    Attributes:
        measured_compound_id (int): Unique identifier for the measured compound.

    Config:
        orm_mode (bool): Enables ORM mode for compatibility with ORMs like 
        SQLAlchemy.
    """
    measured_compound_id: int

    class Config:
        orm_mode = True

class MeasuredCompoundClient(BaseModel):
    """
    MeasuredCompoundClient is a Pydantic model representing a measured compound
    in a client context.

    Attributes:
        compound_id (int): The unique identifier for the compound.
        compound_name (str): The name of the compound.
        retention_time (float): The retention time of the compound.
        retention_time_comment (Optional[str]): An optional comment about 
        the retention time.
        adduct_name (str): The name of the adduct associated with the compound.
    """
    compound_id: int
    compound_name: str
    retention_time: float
    retention_time_comment: str | None = None
    adduct_name: str

class RetentionTimeBase(BaseModel):
    """
    RetentionTimeBase is a Pydantic model that represents the base structure 
    for retention time data.

    Attributes:
        retention_time (float): The retention time value.
        comment (Optional[str]): An optional comment associated with the 
        retention time.
    """
    retention_time: float
    comment: str | None = None

class RetentionTimeCreate(RetentionTimeBase):
    """
    RetentionTimeCreate is a Pydantic model that inherits from RetentionTimeBase.
    This class is used for creating new retention time entries.
    """
    pass

class RetentionTime(RetentionTimeBase):
    """
    RetentionTime model that extends RetentionTimeBase.

    Attributes:
        retention_time_id (int): Unique identifier for the retention time.

    Config:
        orm_mode (bool): Enables ORM mode for compatibility with ORMs like 
        SQLAlchemy.
    """
    retention_time_id: int

    class Config:
        orm_mode = True