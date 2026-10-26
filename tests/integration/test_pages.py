"""Real HTTP requests via FastAPI TestClient, without running YOLO."""
from uuid import uuid4
from fastapi.testclient import TestClient
from app.main import app
from app.db.database import SessionLocal
from app.models.entities import Usuario
from app.core.security import hash_password

c = TestClient(app, base_url="http://testserver")
ORIGIN = {"Origin": "http://testserver"}


def test_login_page():
    assert c.get("/login").status_code == 200


def test_bad_login():
    assert c.post("/login", data={"email": "x@x.com", "password": "bad"}, headers=ORIGIN).status_code == 401


def test_cross_origin_login_rejected():
    assert c.post("/login", data={"email": "x@x.com", "password": "bad"}, headers={"Origin": "https://attacker.invalid"}).status_code == 403


def test_missing_origin_login_rejected():
    assert c.post("/login", data={"email": "x@x.com", "password": "bad"}).status_code == 403


def test_health():
    assert c.get("/health").json()["status"] == "ok"


def test_dashboard_requires_auth():
    assert c.get("/dashboard", follow_redirects=False).status_code in (401, 307, 303)


def test_login_dashboard_logout_roundtrip():
    email = f"integration-{uuid4().hex}@example.test"
    password = "IntegrationPassphrase-2026!"
    db = SessionLocal()
    user = Usuario(nombre="Integration", email=email, password_hash=hash_password(password), rol="ADMIN")
    db.add(user)
    db.commit()
    try:
        with TestClient(app, base_url="http://testserver") as client:
            login = client.post("/login", data={"email": email, "password": password}, headers=ORIGIN, follow_redirects=False)
            assert login.status_code == 303
            assert "sv_session" in login.cookies
            assert client.get("/dashboard").status_code == 200
            assert client.get("/logout", follow_redirects=False).status_code == 303
            assert client.get("/dashboard", follow_redirects=False).status_code in (401, 307, 303)
    finally:
        db.delete(user)
        db.commit()
        db.close()
