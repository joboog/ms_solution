from sqlalchemy import Column, ForeignKey, Integer, String, Float
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property


from .database import Base
from database.chem import parse_and_compute_mass, update_molecular_formula


class Compound(Base):
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
    __tablename__ = "adducts"

    adduct_id = Column(Integer, primary_key=True, index=True)
    adduct_name = Column(String, index=True, nullable=False)
    mass_adjustment = Column(Float, nullable=False)
    ion_mode = Column(String, nullable=False)
    
    measured_compound_a = relationship("MeasuredCompound", back_populates="adduct")
    

class MeasuredCompound(Base):
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
    __tablename__ = "retention_times"

    retention_time_id = Column(Integer, primary_key=True, index=True)
    retention_time = Column(Float, nullable=False)
    comment = Column(String)