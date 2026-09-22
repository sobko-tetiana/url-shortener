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
