
import streamlit as st
import pandas as pd

import ms.io as io

st.title("API Interaction")
api_url="http://127.0.0.1:8000"

# Show a specific item by ID
if st.button("Get Compounds"):
    dataholder1 = io.DataHolder(api_url)
    compounds = dataholder1.get_compounds_from_db()
    compounds_df = pd.DataFrame(compounds)
    st.dataframe(compounds_df)
    
st.markdown("---")
# Define parameters for measured compounds
retention_time = st.text_input("Retention Time", value=None)
compound_type = st.text_input("Type", value=None)
ion_mode = st.text_input("Ion Mode", value=None)

if st.button("Get Measured Compounds"):
    dataholder2 = io.DataHolder(api_url)
    msc = dataholder2.get_measured_compounds_from_db(
        retention_time=retention_time, type=compound_type, ion_mode=ion_mode
    )
    msc_df = pd.DataFrame(msc)
    st.dataframe(msc_df)
    
    
st.markdown("---")
# Define parameters for adding a measured compound
compound_id = st.number_input("Compound ID", value=0, step=1)
compound_name = st.text_input("Compound Name", value=None, key="compound_name")
retention_time = st.number_input("Retention Time", value=0.0, step=0.01)
adduct_name = st.text_input("Adduct Name", value=None, key="adduct_name")
molecular_formula = st.text_input("Molecular Formula", value=None, key="molecular_formula")
retention_time_comment = st.text_input("Retention Time Comment", value=None, key="retention_time_comment")

if st.button("Add Measured Compound"):
    dataholder3 = io.DataHolder(api_url)
    result = dataholder3.add_measured_compound(
        compound_id=compound_id,
        compound_name=compound_name,
        retention_time=retention_time,
        adduct_name=adduct_name,
        molecular_formula=molecular_formula,
        retention_time_comment=retention_time_comment
    )
    dataholder3.insert_measured_compounds_in_db()
    st.write(result)