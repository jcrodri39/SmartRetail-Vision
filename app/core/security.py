from datetime import datetime,timedelta,timezone
import jwt
from pwdlib import PasswordHash
from app.core.config import settings
ph=PasswordHash.recommended()
def hash_password(v):return ph.hash(v)
def verify_password(v,h):return ph.verify(v,h)
def token(uid,role):return jwt.encode({"sub":str(uid),"role":role,"exp":datetime.now(timezone.utc)+timedelta(hours=8)},settings.secret_key,algorithm="HS256")
def decode(v):return jwt.decode(v,settings.secret_key,algorithms=["HS256"])
