import pytest
from gistCheck import app, CACHE


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        # Clear in-memory cache before each test
        CACHE.clear()
        yield client


@pytest.mark.parametrize(
    "username, page, per_page, expected",
    [
        (
            "octocat",
            1,
            5,
            lambda result: isinstance(result["gists"], list)
            and result["page"] == 1
            and result["per_page"] == 5,
        ),
        (
            "nonexistentuser123456789",
            1,
            5,
            lambda result: result["gists"] == [] and result["total"] == 0,
        ),
    ],
)
def test_get_user_gists_default(client, username, page, per_page, expected):
    if page is None and per_page is None:
        response = client.get(f"/{username}")
    else:
        response = client.get(f"/{username}?page={page}&per_page={per_page}")

    assert response.status_code == 200
    assert expected(response.json)


def test_cache_behavior(client):
    # First request: should fetch from GitHub API
    response1 = client.get("/octocat?page=1&per_page=5")
    assert response1.status_code == 200
    assert isinstance(response1.json["gists"], list)
    assert "octocat" in CACHE  # Verify cache was populated

    # Second request: should hit cache
    cached_data = CACHE["octocat"][1]  # Get cached gists
    response2 = client.get("/octocat?page=1&per_page=5")
    assert response2.status_code == 200
    assert (
        response2.json["gists"] == cached_data[:5]
    )  # Check paginated gists match cached data


def test_pagination(client):
    # Test pagination for octocat with different page and per_page values
    per_page = 3
    # First page
    response1 = client.get(f"/octocat?page=1&per_page={per_page}")
    assert response1.status_code == 200
    assert response1.json["page"] == 1
    assert response1.json["per_page"] == per_page
    assert isinstance(response1.json["gists"], list)
    assert (
        len(response1.json["gists"]) <= per_page
    )  # May be less if octocat has fewer gists
    total_gists = response1.json["total"]
    gists_page1 = response1.json["gists"]

    # Second page (if there are enough gists)
    if total_gists > per_page:
        response2 = client.get(f"/octocat?page=2&per_page={per_page}")
        assert response2.status_code == 200
        assert response2.json["page"] == 2
        assert response2.json["per_page"] == per_page
        assert isinstance(response2.json["gists"], list)
        assert len(response2.json["gists"]) <= per_page
        assert response2.json["total"] == total_gists  # Total should be consistent
        # Ensure no overlap between pages
        page1_ids = {gist["id"] for gist in gists_page1}
        page2_ids = {gist["id"] for gist in response2.json["gists"]}
        assert page1_ids.isdisjoint(page2_ids)  # No common gist IDs between pages

    # Test with a different per_page value
    response3 = client.get("/octocat?page=1&per_page=2")
    assert response3.status_code == 200
    assert response3.json["page"] == 1
    assert response3.json["per_page"] == 2
    assert isinstance(response3.json["gists"], list)
    assert len(response3.json["gists"]) <= 2
    assert response3.json["total"] == total_gists  # Total should remain consistent
