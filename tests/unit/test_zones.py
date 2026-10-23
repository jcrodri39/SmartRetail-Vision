import json
from app.analytics.zones import valid_polygon,inside
P=json.dumps([[0,0],[100,0],[100,100],[0,100]])
def test_valid():assert valid_polygon(P)
def test_invalid():assert not valid_polygon("[]")
def test_inside():assert inside(P,(50,50))
def test_outside():assert not inside(P,(150,50))
