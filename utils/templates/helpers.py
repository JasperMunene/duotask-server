def first_name(name: str) -> str:
    """
    Extract the first name from a full name string.
    Example: "Eslieh Victor" -> "Eslieh"
    """
    if not name:
        return "User"
    return name.strip().split()[0].capitalize()
