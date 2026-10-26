import pytest
from app.core.request_origin import normalized_origin, same_origin_request

@pytest.mark.parametrize("origin,ref,expected", [
    ("https://retail.example",None,True),
    ("https://retail.example:443",None,True),
    ("https://evil.example",None,False),
    ("null",None,False),
    (None,"https://retail.example/dashboard",True),
    (None,"https://retail.example.evil.test/dashboard",False),
    (None,None,False),
    ("https://evil.example","https://retail.example/dashboard",False),
    ("http://retail.example",None,False),
    ("https://retail.example/path",None,False),
])
def test_same_origin(origin,ref,expected):
    assert same_origin_request("https://retail.example",origin,ref) is expected

def test_malformed_and_credentials_rejected():
    assert normalized_origin("https://user:pass@retail.example") is None
    assert normalized_origin("javascript:alert(1)") is None
    assert normalized_origin("https://retail.example:bad") is None
