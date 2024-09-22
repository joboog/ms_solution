from sqlalchemy import Column, ForeignKey, Integer, String, Float
from sqlalchemy.orm import relationship
#from sqlalchemy.ext.hybrid import hybrid_property

from .database import Base


class Compound(Base):
    __tablename__ = "compounds"

    compound_id = Column(Integer, primary_key=True, index=True)
    compound_name = Column(String, index=True, nullable=False)
    molecular_formula = Column(String, nullable=False)
    type = Column(String)
    # _computed_mass = Column("computed_mass", Float)  # Store the computed value

    # @hybrid_property
    # def computed_mass(self):
    #     # Define the logic to compute the mass
    #     return some_computation_based_on_other_columns(self.molecular_formula)


class Adduct(Base):
    __tablename__ = "adducts"

    adduct_id = Column(Integer, primary_key=True, index=True)
    adduct_name = Column(String, index=True, nullable=False)
    mass_adjustment = Column(Float, nullable=False)
    ion_mode = Column(String, nullable=False)


class MeasuredCompound(Base):
    __tablename__ = "measured_compounds"

    measured_compound_id = Column(Integer, primary_key=True, index=True)
    compound_id = Column(Integer, ForeignKey("compounds.compound_id"))
    retention_time_id = Column(Integer, ForeignKey("retention_times.retention_time_id"))
    adduct_id = Column(Integer, ForeignKey("adducts.adduct_id"))
    # _measured_mass = Column("measured_mass", Float)  # Store the computed value
    # _molecular_formula = Column("molecular_formula", String)  # Store the computed value

    # @hybrid_property
    # def measured_mass(self):
    #     # Define the logic to compute the measured mass
    #     return some_computation_based_on_other_columns(self.compound_id, self.adduct_id)

    # @hybrid_property
    # def molecular_formula(self):
    #     # Define the logic to compute the molecular formula
    #     return some_computation_based_on_other_columns(self.compound_id)


    compound = relationship("Compound")
    retention_time = relationship("RetentionTime")
    adduct = relationship("Adduct")


class RetentionTime(Base):
    __tablename__ = "retention_times"

    retention_time_id = Column(Integer, primary_key=True, index=True)
    retention_time = Column(Float, nullable=False)
    comment = Column(String)