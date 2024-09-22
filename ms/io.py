import os
import sys

import json
import openpyxl
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from database.pydantic_models import CompoundCreate

class DataHolder:
    def __init__(self, api_url: str):
        self.api_url =  api_url
        self.data = None
        
    def read_in(
      self, 
      file_path_or_str: str,
      unique_cols: list[str] = None,
      dtypes: dict = None
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
          engine='openpyxl'
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
      
      df = df.where(pd.notnull(df), None)  
      print(df)
      print(df.info())        
      data = df.to_dict(orient='records')
      #print(data)
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
        
    def insert_compounds_in_db(self):
        dicts = [model.model_dump() for model in self.data]
        insert_db(self.api_url, "/compounds/", dicts)

