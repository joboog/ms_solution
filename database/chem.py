import re
from pyteomics import mass

def parse_formula(formula):
    """
    Parses a chemical formula and returns a standardized version of it.
    This function takes a chemical formula as input and parses it to identify
    isotopes, elements, and their counts. It then constructs a new formula
    string in a standardized format.
    Args:
        formula (str): The chemical formula to be parsed.
    Returns:
        str: The standardized chemical formula.
    """

    pattern = re.compile(r'(\[\d+\])?([A-Z][a-z]*)(\d*)')
    
    parsed = []
    
    for match in pattern.finditer(formula):
        isotope = match.group(1) or ''
        element = match.group(2)
        count = match.group(3) or '1'
        
        if isotope:
            parsed.append(f"{element}{isotope}{count}")
        else:
            parsed.append(f"{element}{count}")
  
    new_formula = ''.join(parsed)
    
    return new_formula
  

def parse_and_compute_mass(formula):
    """
    Parses a chemical formula and computes its monoisotopic mass.
    Args:
        formula (str): The chemical formula to be parsed and computed.
    Returns:
        float: The monoisotopic mass of the given chemical formula.
    """
    parsed_formula = parse_formula(formula)
    monoisotopic_mass = mass.calculate_mass(formula=parsed_formula)
    
    return monoisotopic_mass

   

def update_molecular_formula(formula, adduct_name):
    """
    Updates the molecular formula based on the given adduct name.
    Args:
        formula (str): The original molecular formula.
        adduct_name (str): The adduct name to modify the formula. 
        Supported values are "M+H", "M-H", and "M+Na".
    Returns:
        str: The updated molecular formula.
    Raises:
        ValueError: If the formula contains invalid elements or counts.
    """
    
    pattern = re.compile(r'([A-Z][a-z]*)(\d*)')
    
    parsed = []
    found_Na = False
    for match in pattern.finditer(formula):
        element = match.group(1)
        count = match.group(2)
        
        if adduct_name in ["M+H"] and element == "H":
            count = str(int(count) + 1)
            parsed.append(f"{element}{count}")
            
        elif adduct_name in ["M-H"] and element == "H":
            count = str(int(count) - 1)
            parsed.append(f"{element}{count}")
        
        elif adduct_name in ["M+Na"] and element == "Na":
            count = str(int(count) + 1)
            parsed.append(f"{element}{count}")
            found_Na=True
        else:
            parsed.append(f"{element}{count}")
    
    if not found_Na and adduct_name in ["M+Na"]:
        parsed.append("Na1")
  
    new_formula = ''.join(parsed)
    
    return new_formula

