import pytest
from flask import Flask
from application import create_app
@pytest.fixture()
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
    })
    yield app

@pytest.fixture()
def client(app):
    return app.test_client()

def test_home_page(client):
        response = client.get('/')
        assert response.status_code == 200
        assert b'<h1>Spotify Data</h1>' in response.data
        assert b"<p class=\"lead\">Don't have a Spotify account? Try a demo!</p>" in response.data

def test_demo(client):
    response = client.get('/demo', follow_redirects=True)
    assert response.status_code == 200
    assert b'<h1>Welcome Guest!</h1>' in response.data

    # Remaining within the context of the first call, testing all other endpoints (until I figure out how to separate them with app context)
    response = client.get('/playlists')
    assert response.status_code == 200
    assert b'<h1>Your playlists:</h1>' in response.data

    response = client.get('/search')
    assert response.status_code == 200
    assert b'<label>Click on the artist image to get an audio analysis!</label>' in response.data

    response = client.get('/content/playlists/2NPt11BnuqkJs4vFcpwVhM')
    assert response.status_code == 200
    assert b'<h1>R&amp;B - 9 tracks | Duration: 37m57s</h1>' in response.data

    response = client.get('/features/4OBZT9EnhYIV17t4pGw7ig')
    assert response.status_code == 200
    assert b'<h3>Best Part (feat. Daniel Caesar)</h3>' in response.data

    response = client.get('/features/4OBZT9EnhYIV17t4pGw7ig119823791287')
    assert response.status_code == 404
    assert b'<h2 class="text-center" style="margin: 15%;">404: Sorry, there was a problem loading that page!</h2>' in response.data