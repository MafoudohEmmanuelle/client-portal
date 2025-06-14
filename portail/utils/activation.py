import hashlib
import time

TOKEN_SALT = 'my_secret_salt'

def generate_activation_token(user):
    """Generate a secure hash token based on user id and a secret salt."""
    timestamp = int(time.time())  # Optional: Can use it to add expiration later
    data = f'{user.pk}{TOKEN_SALT}{timestamp}'
    token = hashlib.sha256(data.encode()).hexdigest()
    return token, timestamp

def verify_activation_token(user, token, timestamp, expiration=3600):
    """Verify if the token is still valid and correctly generated."""
    expected_data = f'{user.pk}{TOKEN_SALT}{timestamp}'
    expected_token = hashlib.sha256(expected_data.encode()).hexdigest()

    if expected_token != token:
        return False

    current_time = int(time.time())
    if current_time - timestamp > expiration:
        return False

    return True
