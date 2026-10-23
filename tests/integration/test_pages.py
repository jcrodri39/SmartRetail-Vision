from fastapi.testclient import TestClient
from app.main import app
c=TestClient(app)
def test_login_page():assert c.get("/login").status_code==200
def test_bad_login():assert c.post("/login",data={"email":"x@x.com","password":"bad"}).status_code==401
def test_health():assert c.get("/health").json()["status"]=="ok"
def test_dashboard_requires_auth():assert c.get("/dashboard",follow_redirects=False).status_code in (401,307,303)
