from httpx import AsyncClient


EXAMPLE_URL = "https://example.com/some/long/path"


async def test_shorten_then_redirect_roundtrip(client: AsyncClient):
    shorten_response = await client.post(
        "/shorten", json={"original_url": EXAMPLE_URL}
    )
    assert shorten_response.status_code == 200
    shortened_url = shorten_response.json()["shortened_url"]
    code = shortened_url.rsplit("/", 1)[-1]

    redirect_response = await client.get(f"/{code}")

    assert redirect_response.status_code == 200
    assert redirect_response.json()["original_url"] == EXAMPLE_URL


async def test_shorten_rejects_invalid_url(client: AsyncClient):
    response = await client.post(
        "/shorten", json={"original_url": "not-a-url"}
    )

    assert response.status_code == 422


async def test_redirect_returns_404_for_unknown_code(client: AsyncClient):
    response = await client.get("/aaaaaaaaaa")

    assert response.status_code == 404


async def _register_and_login(client: AsyncClient, email: str) -> str:
    await client.post(
        "/register", json={"email": email, "password": "password123"}
    )
    login_response = await client.post(
        "/login", json={"email": email, "password": "password123"}
    )
    return login_response.json()["access_token"]


async def test_list_urls_requires_authentication(client: AsyncClient):
    response = await client.get("/urls")

    assert response.status_code == 401


async def test_list_urls_returns_only_own_urls_with_click_counts(
    client: AsyncClient,
):
    access_token = await _register_and_login(client, "owner@example.com")
    headers = {"Authorization": f"Bearer {access_token}"}

    shorten_response = await client.post(
        "/shorten", json={"original_url": EXAMPLE_URL}, headers=headers
    )
    shortened_url = shorten_response.json()["shortened_url"]
    code = shortened_url.rsplit("/", 1)[-1]

    await client.get(f"/{code}")
    await client.get(f"/{code}")

    other_access_token = await _register_and_login(client, "other@example.com")
    await client.post(
        "/shorten",
        json={"original_url": "https://example.com/other"},
        headers={"Authorization": f"Bearer {other_access_token}"},
    )

    list_response = await client.get("/urls", headers=headers)

    assert list_response.status_code == 200
    urls = list_response.json()
    assert len(urls) == 1
    assert urls[0]["original_url"] == EXAMPLE_URL
    assert urls[0]["click_count"] == 2


async def test_delete_url_removes_it_for_owner(client: AsyncClient):
    access_token = await _register_and_login(client, "deleter@example.com")
    headers = {"Authorization": f"Bearer {access_token}"}

    shorten_response = await client.post(
        "/shorten", json={"original_url": EXAMPLE_URL}, headers=headers
    )
    shortened_url = shorten_response.json()["shortened_url"]
    code = shortened_url.rsplit("/", 1)[-1]

    delete_response = await client.delete(f"/urls/{code}", headers=headers)
    assert delete_response.status_code == 200

    list_response = await client.get("/urls", headers=headers)
    assert list_response.json() == []


async def test_delete_url_rejects_non_owner(client: AsyncClient):
    owner_token = await _register_and_login(client, "owns-it@example.com")
    shorten_response = await client.post(
        "/shorten",
        json={"original_url": EXAMPLE_URL},
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    shortened_url = shorten_response.json()["shortened_url"]
    code = shortened_url.rsplit("/", 1)[-1]

    intruder_token = await _register_and_login(client, "intruder@example.com")
    delete_response = await client.delete(
        f"/urls/{code}",
        headers={"Authorization": f"Bearer {intruder_token}"},
    )

    assert delete_response.status_code == 404
