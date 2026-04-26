from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_note_crud(client: AsyncClient) -> None:
    r = await client.post("/notes", json={"title": "T", "body_html": "<p>Hello</p>"})
    assert r.status_code == 201, r.text
    data = r.json()
    nid = data["id"]
    assert data["body_text"] == "Hello"
    g = await client.get(f"/notes/{nid}")
    assert g.status_code == 200
    u = await client.patch(
        f"/notes/{nid}", json={"body_html": "<p>World</p>", "title": "T2"}
    )
    assert u.status_code == 200
    assert u.json()["body_text"] == "World"
    lst = await client.get("/notes?limit=10&offset=0")
    assert lst.status_code == 200
    assert lst.json()["total"] >= 1
    d = await client.delete(f"/notes/{nid}")
    assert d.status_code == 204
    n = await client.get(f"/notes/{nid}")
    assert n.status_code == 404
