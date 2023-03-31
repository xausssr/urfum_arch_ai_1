from fastapi.testclient import TestClient
from main import app
from main import app

client = TestClient(app)


def test_post():
    
    article = client.post("/http://51.250.4.66:5000/send_text")
    assert article == str

def test_get():
    title = client.get("http://51.250.4.66:5000/get_result")
    assert title == str
#x = input()

#def test_light(x):
    #assert x == str