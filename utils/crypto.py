import bcrypt
import base64

def hash_password(password: str) -> str:
    """
    Generate a hashed password using bcrypt.

    Args:
        password (str): The password to hash.

    Returns:
        str: The hashed password.
    """

    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

    return hashed_password.decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hashed version using bcrypt.

    Args:
        password (str): The password to verify.
        hashed_password (str): The hashed password to compare against.

    Returns:
        bool: True if the password matches the hashed password, False otherwise.
    """

    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def decode_cursor(cursor: str) -> int:
    """
    Decode a cursor string back to its original number representation.

    Args:
        cursor (str): The cursor string to decode.

    Returns:
        int: The decoded number.
    """
    # Convert the cursor from string to bytes
    cursor_bytes = cursor.encode('utf-8')
    # Decode the base64-encoded bytes
    decoded_bytes = base64.b64decode(cursor_bytes)
    # Convert the bytes to a string and parse it as an integer
    decoded_number = int(decoded_bytes.decode('utf-8'))
    return decoded_number

def encode_cursor(number: int) -> str:
    """
    Encode a number to a cursor string using base64 encoding.

    Args:
        number (int): The number to encode.

    Returns:
        str: The encoded cursor string.
    """
    # Convert the number to bytes
    number_bytes = str(number).encode('utf-8')
    # Encode the bytes using base64
    encoded_cursor = base64.b64encode(number_bytes)
    # Convert the bytes to a string
    return encoded_cursor.decode('utf-8')



