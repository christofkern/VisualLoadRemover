def duplicate_entry(loads, new_entry):
    """
    Check if a new entry already exists in the loads array.

    Args:
    - loads: The array containing the existing entries.
    - new_entry: The new entry to be checked.

    Returns:
    - True if the new entry already exists in the loads array, False otherwise.
    """
    # Return False if loads is empty
    if not loads:
        return False
    # Convert new_entry to the same format as the entries in loads
    new_entry_converted = tuple(new_entry) if isinstance(loads[0], tuple) else list(new_entry)

    for entry in loads:
        # Convert entry to the same format as new_entry
        entry_converted = tuple(entry) if isinstance(loads[0], tuple) else list(entry)
        if entry_converted == new_entry_converted:
            return True
    return False
