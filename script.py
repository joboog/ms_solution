import ms.io as io

# Populate emtpy database with api

# Read from file and POST compounds
data_holder = io.DataHolder(api_url="http://127.0.0.1:8000") 
data_holder.read_compounds(file_path="data/compounds.xlsx")
data_holder.data
data_holder.insert_compounds_in_db()

# Read from file and POST adducts
data_holder2 = io.DataHolder(api_url="http://127.0.0.1:8000")
data_holder2.read_adducts_from_file(file_path="data/adducts.json")
data_holder2.data
data_holder2.insert_adducts_in_db()

# Read from file and POST measured compounds
data_holder5 = io.DataHolder(api_url="http://127.0.0.1:8000")
data_holder5.read_measured_compounds(file_path="data/measured-compounds.xlsx")
data_holder5.insert_measured_compounds_in_db()


# Show api

# GET compounds
data_holder6 = io.DataHolder(api_url="http://127.0.0.1:8000")
data_holder6.get_compounds_from_db()

# GET measured compounds
data_holder6.get_measured_compounds_from_db()

# GET measured compounds with query params
data_holder6.get_measured_compounds_from_db(
  retention_time=5.31, type="metabolite", ion_mode="positive"
)

# POST measured compound
data_holder7= io.DataHolder(api_url="http://127.0.0.1:8000")

data_holder7.add_measured_compound(
  compound_id=7,
  compound_name="MCPA-D6",
  retention_time=11.31,
  retention_time_comment="difficult to measure",
  adduct_name="M+H",
  molecular_formula="C9H3[2]H6O3Cl1"
)
data_holder7.insert_measured_compounds_in_db()

# GET this measured compound
data_holder7.get_measured_compounds_from_db(
  retention_time=11.31, type=None, ion_mode="positive"
)
