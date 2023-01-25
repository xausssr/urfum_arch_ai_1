from app import app


def test_main_page():
    response = app.test_client().get('/')
    assert response.status_code == 200
    assert response.content_type == 'text/html; charset=utf-8'


def test_send_text():
    response = app.test_client().post('/send_text')
    assert response.status_code == 200
    assert response.content_length == 64
    global id
    id = response.get_data(as_text=True)
    

def test_get_page():
    response = app.test_client().get('/get_result?id='+str(id))
    assert response.status_code == 204
