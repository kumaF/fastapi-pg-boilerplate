from passlib.context import CryptContext

pwd_context = CryptContext(
    # append the hash(es) list you wish to support.
    schemes=['argon2'],
    # if not mentioned it will use the first hasher in the schemes list.
    default='argon2',
    # either you can specify hasher list you need to depricate
    # or 'auto' mark all but first hasher in schemes list as deprecated
    deprecated='auto'
)


async def hash_password(password: str) -> str:
    return pwd_context.hash(secret=password)


async def verify_password(password: str, hashed_password: str) -> tuple[bool, str | None]:
    is_verified, updated_password = pwd_context.verify_and_update(
        secret=password,
        hash=hashed_password
    )

    return is_verified, updated_password
