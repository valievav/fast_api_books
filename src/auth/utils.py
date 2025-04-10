from passlib.context import CryptContext

password_context = CryptContext(
    schemes=['bcrypt']
)


def generate_password_hash(password: str) -> str:
    hash = password_context.hash(password)
    return hash

def verify_password(password: str, hash: str) -> bool:
    match = password_context.verify(password, hash)
    return match
