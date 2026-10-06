from datetime import datetime,timedelta,timezone
import jwt
from passlib.context import CryptContext
from .config import settings
pwd=CryptContext(schemes=["bcrypt"],deprecated="auto")
def hash_password(v): return pwd.hash(v)
def verify_password(v,h): return pwd.verify(v,h)
def token(uid):
    return jwt.encode({"sub":str(uid),"exp":datetime.now(timezone.utc)+timedelta(hours=24)},settings.secret_key,algorithm="HS256")
