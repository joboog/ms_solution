import os
import sys

import json
import openpyxl
import pandas as pd
import requests

from .utils import is_valid_json, check_unique_cols

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from database.pydantic_models import CompoundCreate, AdductCreate, \
    MeasuredCompoundClient

class DataHolder:
    def __init__(self, api_url: str):
        """
        Initializes the instance with the given API URL.

        Args:
          api_url (str): The URL of the API to connect to.
        """
        self.api_url =  api_url
        self.data = None
        
    def read_in(
      self, 
      file_path_or_str: str,
      unique_cols: list[str] = None,
      dtypes: dict = None,
      use_cols: list[str] = None,
      new_colnames: dict = None
      ) -> pd.DataFrame:
      """
      Reads data from a JSON or Excel file and returns it as a pandas DataFrame.
      Args:
        file_path_or_str (str): Path to the file or a JSON string.
        unique_cols (list[str], optional): List of columns that should be unique. Defaults to None.
        dtypes (dict, optional): Dictionary specifying the data types of columns. Defaults to None.
        use_cols (list[str], optional): List of columns to read from the file. Defaults to None.
        new_colnames (dict, optional): Dictionary for renaming columns. Defaults to None.
      Returns:
        pd.DataFrame: DataFrame containing the data from the file.
      Raises:
        ValueError: If the file type is not supported.
      """
      
      if file_path_or_str.endswith('.json') or is_valid_json(file_path_or_str):
        df = pd.read_json(
          file_path_or_str, 
          orient="records", 
          typ="frame", 
          dtype=dtypes
        )
        
      elif file_path_or_str.endswith('.xlsx') or file_path_or_str.endswith('.xls'):
        df = pd.read_excel(
          file_path_or_str, 
          dtype=dtypes, 
          engine='openpyxl',
          usecols=use_cols
        )
        
      else:
        raise ValueError(
        """Unsupported file type. Please provide a .json or 
        .xlsx/.xls file.
        """
        )
        
      if unique_cols is not None:
        check_unique_cols(df, unique_cols)
      
      if new_colnames is not None:
        df = df.rename(columns=new_colnames)
      
      df = df.where(pd.notnull(df), None)
      return df
    
    def read_compounds(self, file_path: str) -> list[CompoundCreate]:
        """
        Reads compound data from a file and returns a list of CompoundCreate objects.

        Args:
            file_path (str): The path to the file containing compound data.

        Returns:
            list[CompoundCreate]: A list of CompoundCreate objects.

        """
        dtypes = {
            "compound_id": "Int64",
            "compound_name": "string",
            "molecular_formula": "string",
            "type": "string"
        }
        df = self.read_in(
          file_path, unique_cols=['compound_id'], dtypes=dtypes
        )
        data = df.to_dict(orient='records')
        self.data = [CompoundCreate(**compound) for compound in data]
     
     
    def read_adducts_from_file(self, file_path: str) -> list[AdductCreate]:
        """
        Reads adduct data from a specified file and returns a list of AdductCreate objects.

        Args:
            file_path (str): The path to the file containing adduct data.

        Returns:
            list[AdductCreate]: A list of AdductCreate objects populated with data from the file.

        Raises:
            FileNotFoundError: If the specified file does not exist.
            ValueError: If the data in the file is not in the expected format.

        """
        dtypes = {
            "name": "string",
            "mass": "float",
            "ion_mode": "string"
        }
        new_cols = {
          "name": "adduct_name",
          "mass": "mass_adjustment"
        }
        df = self.read_in(
          file_path, unique_cols=['name'], dtypes=dtypes, new_colnames=new_cols
        )
        data = df.to_dict(orient='records')
        self.data = [AdductCreate(**adduct) for adduct in data]
        
    
    def read_adducts_from_json(self, json_str: str) -> list[AdductCreate]:
        """
        Reads adduct data from a JSON string and converts it into a list of AdductCreate objects.

        Args:
            json_str (str): A JSON string containing adduct data.

        Returns:
            list[AdductCreate]: A list of AdductCreate objects created from the JSON data.
        """
        dtypes = {
            "adduct_name": "string",
            "mass_adjustment": "float",
            "ion_mode": "string"
        }
        df = self.read_in(
          json_str, unique_cols=['adduct_name'], dtypes=dtypes
        )
        data = df.to_dict(orient='records')
        self.data = [AdductCreate(**adduct) for adduct in data]
        
    
    def read_measured_compounds(
        self, 
        file_path: str
        ) -> list[MeasuredCompoundClient]:
        """
        Reads measured compounds from a specified file and returns a list of MeasuredCompoundClient objects.

        Args:
            file_path (str): The path to the file containing the measured compounds data.

        Returns:
            list[MeasuredCompoundClient]: A list of MeasuredCompoundClient objects populated with the data from the file.
        """
      
        dtypes = {
            "compound_id": "Int64",
            "compound_name": "string",
            "retention_time": "float",
            "retention_time_comment": "string",
            "adduct_name": "string",
            "molecular_formula": "string"
        }
        use_cols = ["compound_id", "compound_name", "retention_time", 
            "retention_time_comment", "adduct_name", "molecular_formula"]
        df = self.read_in(file_path, dtypes=dtypes, use_cols=use_cols)
        data = df.to_dict(orient='records')    
        self.data = [MeasuredCompoundClient(**mc) for mc in data]
        
    def add_measured_compound(
        self,
        compound_id: int,
        compound_name: str,
        retention_time: float,
        adduct_name: str,
        molecular_formula: str,
        retention_time_comment: str | None = None
    ):
        """
        Adds a measured compound to the data list.

        Parameters:
        - compound_id (int): The unique identifier for the compound.
        - compound_name (str): The name of the compound.
        - retention_time (float): The retention time of the compound.
        - adduct_name (str): The name of the adduct.
        - molecular_formula (str): The molecular formula of the compound.
        - retention_time_comment (str | None, optional): Additional comments on the retention time. Defaults to None.

        Returns:
        None
        """
        mc = MeasuredCompoundClient(
          compound_id=compound_id,
          compound_name=compound_name,
          retention_time=retention_time,
          retention_time_comment=retention_time_comment,
          adduct_name=adduct_name,
          molecular_formula=molecular_formula
        )
        self.data = [mc]
        
    
    def insert_compounds_in_db(self):
        assert all([isinstance(model, CompoundCreate) for model in self.data])
        dicts = [model.model_dump() for model in self.data]
        insert_db(self.api_url, "/compounds/", dicts)
        
    def insert_adducts_in_db(self):
        assert all([isinstance(model, AdductCreate) for model in self.data])
        dicts = [model.model_dump() for model in self.data]
        insert_db(self.api_url, "/adducts/", dicts)
        
    def insert_measured_compounds_in_db(self):
        assert all([
          isinstance(model, MeasuredCompoundClient) for model in self.data
        ])
        dicts = [model.model_dump() for model in self.data]
        insert_db(self.api_url, "/measured_compounds/", dicts)
        
    def get_compounds_from_db(self):
        return get_from_db(self.api_url, "/compounds/")
    
    def get_measured_compounds_from_db(
      self, 
      retention_time: float | None = None, 
      type: str | None = None,
      ion_mode: str | None = None
      ):
      params = {
        "retention_time": retention_time,
        "type": type,
        "ion_mode": ion_mode
      }
      
      return get_from_db(self.api_url, "/measured_compounds/", params)


# Client db api
def insert_db(api_url, endpoint, dicts = list[dict]):
    """
    Inserts a list of dictionaries into a database via a POST request to the specified API endpoint.
    Args:
      api_url (str): The base URL of the API.
      endpoint (str): The specific endpoint to which the data should be posted.
      dicts (list[dict]): A list of dictionaries containing the data to be inserted.
    Returns:
      dict: The JSON response from the API if the request is successful.
    Raises:
      Exception: If the POST request fails (i.e., the status code is not 200), an exception is raised with the error message from the response.
    """
    assert all([type(x) == dict for x in dicts])
    assert type(api_url) == str
    assert type(endpoint) == str
    
    url = api_url + endpoint
    print(url)
    response = requests.post(url, json=dicts)
    if response.status_code != 200:
        raise Exception(f"Failed to insert {endpoint}: {response.text}")
    return response.json()


def get_from_db(base_url, endpoint, params=None):
    """
    Fetch data from a database endpoint.

    Args:
      base_url (str): The base URL of the database.
      endpoint (str): The specific endpoint to query.
      params (dict, optional): A dictionary of query parameters to include in the request. Defaults to None.

    Returns:
      dict: The JSON response from the database.

    Raises:
      Exception: If the request fails or the response status code is not 200.
    """
    assert [type(x) == str for x in [base_url, endpoint]]
    url = base_url + endpoint
    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise Exception(f"Failed to get data: {response.text}")
    return response.json()
  