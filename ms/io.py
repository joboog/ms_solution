import os
import sys

import json
import openpyxl
import pandas as pd
import requests

from .utils import is_valid_json

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from database.pydantic_models import CompoundCreate, AdductCreate, \
    RetentionTimeCreate

class DataHolder:
    def __init__(self, api_url: str):
        self.api_url =  api_url
        self.data = None
        
    def read_in(
      self, 
      file_path_or_str: str,
      unique_cols: list[str] = None,
      dtypes: dict = None,
      use_cols: list[str] = None,
      new_colnames: dict = None
      ) -> list[dict]:
      
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
        non_unique_cols = [
          col for col in unique_cols 
          if len(df[col].unique()) != len(df[col])
        ]
        if len(non_unique_cols) > 0:
          raise ValueError(
            f"Duplicates in columns {non_unique_cols} are not allowed."
          )
      
      if new_colnames is not None:
        df = df.rename(columns=new_colnames)
      
      df = df.where(pd.notnull(df), None)       
      data = df.to_dict(orient='records')
      return data
    
    def read_compounds(self, file_path: str) -> list[CompoundCreate]:
        dtypes = {
            "compound_id": "Int64",
            "compound_name": "string",
            "molecular_formula": "string",
            "type": "string"
        }
        data = self.read_in(
          file_path, unique_cols=['compound_id'], dtypes=dtypes
        )
        self.data = [CompoundCreate(**compound) for compound in data]
     
     
    def read_adducts_from_file(self, file_path: str) -> list[AdductCreate]:
        dtypes = {
            "name": "string",
            "mass": "float",
            "ion_mode": "string"
        }
        new_cols = {
          "name": "adduct_name",
          "mass": "mass_adjustment"
        }
        data = self.read_in(
          file_path, unique_cols=['name'], dtypes=dtypes, new_colnames=new_cols
        )
            
        self.data = [AdductCreate(**adduct) for adduct in data]
        
    
    def read_adducts_from_json(self, json_str: str) -> list[AdductCreate]:
        dtypes = {
            "adduct_name": "string",
            "mass_adjustment": "float",
            "ion_mode": "string"
        }
        data = self.read_in(
          json_str, unique_cols=['adduct_name'], dtypes=dtypes
        )
        self.data = [AdductCreate(**adduct) for adduct in data]
        
        
    def read_retenion_times(self, file_path: str) -> list[dict]:
        dtypes = {
            "retention_time": "float",
            "retention_time_comment": "string"
        }
        cols = ["retention_time", "retention_time_comment"]
        new_colnames = {"retention_time_comment": "comment"}
        data = self.read_in(file_path, dtypes=dtypes, use_cols=cols, 
                            new_colnames=new_colnames)
        self.data = [RetentionTimeCreate(**rt) for rt in data]
    
    
    def insert_compounds_in_db(self):
        assert all([isinstance(model, CompoundCreate) for model in self.data])
        dicts = [model.model_dump() for model in self.data]
        insert_db(self.api_url, "/compounds/", dicts)
        
    def insert_adducts_in_db(self):
        assert all([isinstance(model, AdductCreate) for model in self.data])
        dicts = [model.model_dump() for model in self.data]
        insert_db(self.api_url, "/adducts/", dicts)
    
    def insert_retention_times_in_db(self):
        assert all([
          isinstance(model, RetentionTimeCreate) for model in self.data
        ])
        dicts = [model.model_dump() for model in self.data]
        insert_db(self.api_url, "/retention_times/", dicts)


# Client db api
def insert_db(api_url, endpoint, dicts = list[dict]):
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
    assert [type(x) == str for x in [base_url, endpoint]]
    url = base_url + endpoint
    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise Exception(f"Failed to get data: {response.text}")
    return response.json()


def is_valid_json(json_str: str) -> bool:
    try:
        json.loads(json_str)
        return True
    except json.JSONDecodeError:
        return False