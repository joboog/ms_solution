import re
from pyteomics import mass


def parse_formula(formula):

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
    parsed_formula = parse_formula(formula)
    monoisotopic_mass = mass.calculate_mass(formula=parsed_formula)
    
    return monoisotopic_mass
