from datetime import datetime,timedelta,timezone
import jwt
try:
    from pwdlib import PasswordHash
except ImportError:
    # argon2-cffi is the underlying Argon2id implementation.
    # Keep the same PHC password-hash format for existing accounts.
    from argon2 import PasswordHasher
    from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHashError

    class PasswordHash:
        @staticmethod
        def recommended():
            hasher = PasswordHasher()

            class Argon2Adapter:
                def hash(self, password):
                    return hasher.hash(password)

                def verify(self, password, stored_hash):
                    try:
                        return hasher.verify(stored_hash, password)
                    except (VerifyMismatchError, VerificationError, InvalidHashError):
                        return False

            return Argon2Adapter()
from app.core.config import settings
ph=PasswordHash.recommended()
def hash_password(v):return ph.hash(v)
def verify_password(v,h):return ph.verify(v,h)
def token(uid,role):return jwt.encode({"sub":str(uid),"role":role,"exp":datetime.now(timezone.utc)+timedelta(hours=8)},settings.secret_key,algorithm="HS256")
def decode(v):return jwt.decode(v,settings.secret_key,algorithms=["HS256"])
