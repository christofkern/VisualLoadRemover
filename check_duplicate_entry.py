def duplicate_entry(loads, new_entry):
    """
    Check if a new entry already exists in the loads array.
    
    Args:
    - loads: The array containing the existing entries.
    - new_entry: The new entry to be checked.
    
    Returns:
    - True if the new entry already exists in the loads array, False otherwise.
    """
    for entry in loads:
        if entry == new_entry:
            return True
    return False
