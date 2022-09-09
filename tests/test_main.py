import pytest
import pytest_asyncio

from httpx import AsyncClient
import starlette.status
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from todo.db import get_db, Base
from todo.main import app

ASYNC_DB_URL = "sqlite+aiosqlite:///:memory:"

@pytest_asyncio.fixture
async def async_client() -> AsyncClient:
    # Async用のengineとsessionを作成
    async_engine = create_async_engine(ASYNC_DB_URL, echo=True)
    async_session = sessionmaker(
        autocommit=False, autoflush=False, bind=async_engine, class_=AsyncSession
    )

    # テスト用にオンメモリのSQLiteテーブルを初期化（関数ごとにリセット）
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # DIを使ってFastAPIのDBの向き先をテスト用DBに変更
    async def get_test_db():
        async with async_session() as session:
            yield session

    app.dependency_overrides[get_db] = get_test_db

    # テスト用に非同期HTTPクライアントを返却
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.mark.asyncio
async def test_create_and_read_and_delete(async_client):
    res = await async_client.post("/tasks", json={"title": "テストタスク"})
    assert res.status_code == starlette.status.HTTP_200_OK
    res_json = res.json()
    assert res_json["title"] == "テストタスク"

    res = await async_client.get("/tasks")
    assert res.status_code == starlette.status.HTTP_200_OK
    res_json = res.json()
    assert res_json[0]["id"] == 1
    assert res_json[0]["title"] == "テストタスク"
    assert res_json[0]["done"] == False
    
    res = await async_client.delete("/tasks/1")
    assert res.status_code == starlette.status.HTTP_200_OK
    res = await async_client.get("/tasks")
    assert res.status_code == starlette.status.HTTP_200_OK
    assert res.json() == []

@pytest.mark.asyncio
async def test_task_update(async_client):
    res = await async_client.post("/tasks", json={"title": "テストタスク変更前"})
    assert res.status_code == starlette.status.HTTP_200_OK
    res_json = res.json()
    assert res.json() == {
        "id": 1,
        "title": "テストタスク変更前",
    }

    res = await async_client.put("/tasks/1", json={"title": "テストタスク変更後"})
    assert res.status_code == starlette.status.HTTP_200_OK
    assert res.json() == {
        "id": 1,
        "title": "テストタスク変更後",
    }

@pytest.mark.asyncio
async def test_done(async_client):
    res = await async_client.post("/tasks", json={"title": "テストタスク"})
    assert res.status_code == starlette.status.HTTP_200_OK
    res = await async_client.get("/tasks")
    assert res.status_code == starlette.status.HTTP_200_OK
    assert res.json() == [{
        "id": 1,
        "title": "テストタスク",
        "done": False,
    }]


    res = await async_client.put("/tasks/1/done")
    assert res.status_code == starlette.status.HTTP_200_OK
    res = await async_client.get("/tasks")
    assert res.status_code == starlette.status.HTTP_200_OK
    assert res.json() == [{
        "id": 1,
        "title": "テストタスク",
        "done": True,
    }]

    res = await async_client.delete("/tasks/1/done")
    assert res.status_code == starlette.status.HTTP_200_OK
    res = await async_client.get("/tasks")
    assert res.status_code == starlette.status.HTTP_200_OK
    assert res.json() == [{
        "id": 1,
        "title": "テストタスク",
        "done": False,
    }]
    
@pytest.mark.asyncio
async def test_delete(async_client):
    res = await async_client.post("/tasks", json={"title": "テストタスク"})
    assert res.status_code == starlette.status.HTTP_200_OK
    res = await async_client.put("/tasks/1/done")
    assert res.status_code == starlette.status.HTTP_200_OK
    res = await async_client.get("/tasks")
    assert res.status_code == starlette.status.HTTP_200_OK
    assert res.json() == [{
        "id": 1,
        "title": "テストタスク",
        "done": True,
    }]
    
    res = await async_client.delete("/tasks/1")
    assert res.status_code == starlette.status.HTTP_200_OK
    res = await async_client.get("/tasks")
    assert res.status_code == starlette.status.HTTP_200_OK
    assert res.json() == []