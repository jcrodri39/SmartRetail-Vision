from app.core.security import hash_password,verify_password,token,decode
def test_hash():h=hash_password("Secret123*");assert verify_password("Secret123*",h);assert not verify_password("x",h)
def test_token():assert decode(token(1,"ADMIN"))["role"]=="ADMIN"
