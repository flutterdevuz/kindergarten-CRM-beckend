import secrets
import string

def generate_custom_id():
    """
    Generates a complex random string ID of 32 characters,
    consisting of lowercase letters and digits.
    Example: hukgvyjfcdrxtrcytfvugybhuniuvcf5
    """
    characters = string.ascii_lowercase + string.digits
    return ''.join(secrets.choice(characters) for _ in range(32))
