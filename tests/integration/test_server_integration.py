def test_index_page_loads(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"GUDLFT Registration Portal" in response.data


def test_valid_login_shows_summary(client):
    response = client.post("/showSummary", data={"email": "john@simplylift.co"})

    assert response.status_code == 200
    assert b"Welcome, john@simplylift.co" in response.data
    assert b"Spring Festival" in response.data
    assert b"Points available: 13" in response.data


def test_purchase_places_deducts_points_and_places_per_requirement(client):
    response = client.post(
        "/purchasePlaces",
        data={
            "competition": "Spring Festival",
            "club": "Simply Lift",
            "places": "3",
        },
    )

    assert response.status_code == 200
    assert b"Great-booking complete!" in response.data
    assert b"Number of Places: 22" in response.data
    assert b"Points available: 10" in response.data


def test_purchase_rejects_more_than_twelve_places(client):
    response = client.post(
        "/purchasePlaces",
        data={
            "competition": "Spring Festival",
            "club": "Simply Lift",
            "places": "13",
        },
    )

    assert response.status_code == 200
    assert b"Great-booking complete!" not in response.data
    assert b"12" in response.data


def test_purchase_rejects_more_places_than_available(client, server_module):
    server_module.competitions[0]["numberOfPlaces"] = "2"

    response = client.post(
        "/purchasePlaces",
        data={
            "competition": "Spring Festival",
            "club": "Simply Lift",
            "places": "3",
        },
    )

    assert response.status_code == 200
    assert b"Great-booking complete!" not in response.data
    assert b"Number of Places: 2" in response.data
