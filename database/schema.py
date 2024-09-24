from sqlalchemy import Column, ForeignKey, Integer, String, Float
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property


from .database import Base
from database.chem import parse_and_compute_mass, update_molecular_formula


class Compound(Base):
    """
    Represents a chemical compound in the database.
    Attributes:
        compound_id (int): The primary key for the compound.
        compound_name (str): The name of the compound.
        molecular_formula (str): The molecular formula of the compound.
        type (str): The type/category of the compound.
        measured_compound_c (relationship): Relationship to the MeasuredCompound model.
    Properties:
        computed_mass (float): The computed mass of the compound based on its 
        molecular formula.
    """
    __tablename__ = "compounds"

    compound_id = Column(Integer, primary_key=True, index=True, nullable=False)
    compound_name = Column(String, index=True, nullable=False)
    molecular_formula = Column(String, nullable=False)
    type = Column(String)
    
    measured_compound_c = relationship(
        "MeasuredCompound", back_populates="compound"
    )

    @hybrid_property # For computing on the Compound instance
    def computed_mass(self):
        return parse_and_compute_mass(self.molecular_formula)

    @computed_mass.expression
    def computed_mass(cls):
        return parse_and_compute_mass(cls.molecular_formula)
    

class Adduct(Base):
    """
    Represents an adduct in the database.
    Attributes:
        adduct_id (int): The primary key for the adduct.
        adduct_name (str): The name of the adduct.
        mass_adjustment (float): The mass adjustment value for the adduct.
        ion_mode (str): The ion mode associated with the adduct.
        measured_compound_a (relationship): Relationship to the MeasuredCompound model.
    """
    __tablename__ = "adducts"

    adduct_id = Column(Integer, primary_key=True, index=True)
    adduct_name = Column(String, index=True, nullable=False)
    mass_adjustment = Column(Float, nullable=False)
    ion_mode = Column(String, nullable=False)
    
    measured_compound_a = relationship(
        "MeasuredCompound", back_populates="adduct"
    )
    

class MeasuredCompound(Base):
    """
    MeasuredCompound is a SQLAlchemy ORM model representing a measured compound
    in the database.
    Attributes:
        measured_compound_id (int): Primary key for the measured compound.
        compound_id (int): Foreign key referencing the compound.
        retention_time_id (int): Foreign key referencing the retention time.
        adduct_id (int): Foreign key referencing the adduct.
        molecular_formula_c (str): Computed molecular formula of the compound.
    Relationships:
        compound (Compound): Relationship to the Compound model.
        retention_time (RetentionTime): Relationship to the RetentionTime model.
        adduct (Adduct): Relationship to the Adduct model.
    Properties:
        molecular_formula_c (str): Hybrid property to get the molecular formula
        from the compound.
        molecular_formula (str): Hybrid property to compute the molecular formula
        using the compound and adduct.
        measured_mass (float): Hybrid property to compute the measured mass 
        from the molecular formula.
    Methods:
        molecular_formula_c.expression: SQL expression for querying the 
        molecular formula.
        molecular_formula_c.setter: Setter for the molecular formula.
        molecular_formula.expression: SQL expression for querying the 
        computed molecular formula.
        measured_mass.expression: SQL expression for querying the computed 
        measured mass.
    """
    __tablename__ = "measured_compounds"

    measured_compound_id = Column(Integer, primary_key=True, index=True)
    compound_id = Column(Integer, ForeignKey("compounds.compound_id"))
    retention_time_id = Column(Integer, ForeignKey("retention_times.retention_time_id"))
    adduct_id = Column(Integer, ForeignKey("adducts.adduct_id"))
    #_measured_mass = Column("measured_mass", Float)
    molecular_formula_c = Column("molecular_formula_c", String)  # Store the computed value

    compound = relationship("Compound", back_populates="measured_compound_c")
    retention_time = relationship("RetentionTime")
    adduct = relationship("Adduct", back_populates="measured_compound_a"
    )
    
    @hybrid_property
    def molecular_formula_c(self):
        if self.compound:
            return self.compound.molecular_formula
        return None

    @molecular_formula_c.expression
    def molecular_formula_c(cls):
        return Compound.molecular_formula
    
    @molecular_formula_c.setter
    def molecular_formula_c(self, value):
        self.molecular_formula_c = value
        
    @hybrid_property
    def molecular_formula(self):
        if self.compound and self.adduct:
            return update_molecular_formula(self.compound.molecular_formula, self.adduct.adduct_name)
        return None

    @molecular_formula.expression
    def molecular_formula(cls):
        return update_molecular_formula(Compound.molecular_formula, Adduct.adduct_name)
    
    @hybrid_property
    def measured_mass(self):
        if self.molecular_formula_c:
            return parse_and_compute_mass(self.molecular_formula_c)
        return None

    @measured_mass.expression
    def measured_mass(cls):
        if Compound:
            return parse_and_compute_mass(cls.molecular_formula_c)
        return None    


class RetentionTime(Base):
    """
    Represents the retention times in the database.

    Attributes:
        retention_time_id (int): The primary key for the retention time entry.
        retention_time (float): The retention time value.
        comment (str): An optional comment about the retention time.
    """
    __tablename__ = "retention_times"

    retention_time_id = Column(Integer, primary_key=True, index=True)
    retention_time = Column(Float, nullable=False)
    comment = Column(String)