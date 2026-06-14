import json
from unittest.mock import mock_open


def _capture_template(monkeypatch, server_module):
    captured = {}

    def fake_render(template_name, **context):
        captured["template"] = template_name
        captured["context"] = context
        return captured

    monkeypatch.setattr(server_module, "render_template", fake_render)
    return captured


def test_load_clubs_reads_clubs_json(monkeypatch, server_module):
    expected_clubs = [{"name": "Unit Club", "email": "unit@example.com", "points": "9"}]
    mocked_open = mock_open(read_data=json.dumps({"clubs": expected_clubs}))
    monkeypatch.setattr("builtins.open", mocked_open)

    assert server_module.loadClubs() == expected_clubs
    mocked_open.assert_called_once_with("clubs.json")


def test_load_competitions_reads_competitions_json(monkeypatch, server_module):
    expected_competitions = [{"name": "Unit Competition", "numberOfPlaces": "7"}]
    mocked_open = mock_open(read_data=json.dumps({"competitions": expected_competitions}))
    monkeypatch.setattr("builtins.open", mocked_open)

    assert server_module.loadCompetitions() == expected_competitions
    mocked_open.assert_called_once_with("competitions.json")


def test_index_renders_login_page(monkeypatch, server_module):
    captured = _capture_template(monkeypatch, server_module)

    result = server_module.index()

    assert result is captured
    assert captured["template"] == "index.html"
    assert captured["context"] == {}


def test_show_summary_strips_whitespace_from_email(monkeypatch, server_module):
    captured = _capture_template(monkeypatch, server_module)

    with server_module.app.test_request_context(
        "/showSummary",
        method="POST",
        data={"email": " john@simplylift.co "},
    ):
        result = server_module.showSummary()

    assert result is captured
    assert captured["template"] == "welcome.html"
    assert captured["context"]["club"]["name"] == "Simply Lift"
    assert captured["context"]["competitions"] == server_module.competitions


def test_show_summary_flashes_when_email_is_unknown(monkeypatch, server_module):
    captured = _capture_template(monkeypatch, server_module)
    flashed_messages = []
    monkeypatch.setattr(server_module, "flash", flashed_messages.append)

    with server_module.app.test_request_context(
        "/showSummary",
        method="POST",
        data={"email": "missing@example.com"},
    ):
        result = server_module.showSummary()

    assert result is captured
    assert captured["template"] == "index.html"
    assert flashed_messages == ["Sorry, that email wasn't found."]


def test_show_summary_treats_missing_email_as_unknown(monkeypatch, server_module):
    captured = _capture_template(monkeypatch, server_module)
    flashed_messages = []
    monkeypatch.setattr(server_module, "flash", flashed_messages.append)

    with server_module.app.test_request_context("/showSummary", method="POST", data={}):
        result = server_module.showSummary()

    assert result is captured
    assert captured["template"] == "index.html"
    assert flashed_messages == ["Sorry, that email wasn't found."]


def test_book_renders_selected_competition_and_club(monkeypatch, server_module):
    captured = _capture_template(monkeypatch, server_module)

    result = server_module.book("Spring Festival", "Simply Lift")

    assert result is captured
    assert captured["template"] == "booking.html"
    assert captured["context"]["club"]["name"] == "Simply Lift"
    assert captured["context"]["competition"]["name"] == "Spring Festival"


def test_purchase_places_decreases_available_places(monkeypatch, server_module):
    captured = _capture_template(monkeypatch, server_module)
    flashed_messages = []
    monkeypatch.setattr(server_module, "flash", flashed_messages.append)

    with server_module.app.test_request_context(
        "/purchasePlaces",
        method="POST",
        data={
            "competition": "Spring Festival",
            "club": "Simply Lift",
            "places": "3",
        },
    ):
        result = server_module.purchasePlaces()

    remaining_places = next(
        competition["numberOfPlaces"]
        for competition in server_module.competitions
        if competition["name"] == "Spring Festival"
    )

    assert result is captured
    assert captured["template"] == "welcome.html"
    assert captured["context"]["club"]["name"] == "Simply Lift"
    assert flashed_messages == ["Great-booking complete!"]
    assert remaining_places == 22


def test_purchase_places_only_updates_selected_competition(monkeypatch, server_module):
    _capture_template(monkeypatch, server_module)
    monkeypatch.setattr(server_module, "flash", lambda _message: None)

    with server_module.app.test_request_context(
        "/purchasePlaces",
        method="POST",
        data={
            "competition": "Fall Classic",
            "club": "She Lifts",
            "places": "2",
        },
    ):
        server_module.purchasePlaces()

    spring_places = next(
        competition["numberOfPlaces"]
        for competition in server_module.competitions
        if competition["name"] == "Spring Festival"
    )
    fall_places = next(
        competition["numberOfPlaces"]
        for competition in server_module.competitions
        if competition["name"] == "Fall Classic"
    )

    assert spring_places == "25"
    assert fall_places == 11


def test_logout_redirects_back_to_index(server_module):
    with server_module.app.test_request_context("/logout"):
        response = server_module.logout()

    assert response.status_code == 302
    assert response.location.endswith("/")
