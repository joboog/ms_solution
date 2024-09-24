import json
import pandas as pd

def is_valid_json(json_str: str) -> bool:
    """
    Checks if a given string is a valid JSON.

    Args:
      json_str (str): The string to be checked.

    Returns:
      bool: True if the string is a valid JSON, False otherwise.
    """
    try:
        json.loads(json_str)
        return True
    except json.JSONDecodeError:
        return False
    
def check_unique_cols(df, unique_cols):
    """
    Checks if the specified columns in the DataFrame have unique values.

    Args:
      df (pandas.DataFrame): The DataFrame to check.
      unique_cols (list of str): List of column names to check for uniqueness.

    Raises:
      ValueError: If any of the specified columns contain duplicate values.

    Returns:
      bool: True if all specified columns have unique values.
    """
    non_unique_cols = [
          col for col in unique_cols 
          if len(df[col].unique()) != len(df[col])
        ]
    if len(non_unique_cols) > 0:
      raise ValueError(
        f"Duplicates in columns {non_unique_cols} are not allowed."
      )
    return True