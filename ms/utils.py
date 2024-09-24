import json
import pandas as pd

def is_valid_json(json_str: str) -> bool:
    try:
        json.loads(json_str)
        return True
    except json.JSONDecodeError:
        return False
    
def check_unique_cols(df, unique_cols):
    non_unique_cols = [
          col for col in unique_cols 
          if len(df[col].unique()) != len(df[col])
        ]
    if len(non_unique_cols) > 0:
      raise ValueError(
        f"Duplicates in columns {non_unique_cols} are not allowed."
      )
    return True