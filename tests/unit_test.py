import uuid
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from main import app
from models import OrderUpdate, OrderClose, MenuItem

client = TestClient(app)


@pytest.fixture
def mock_db():
    with patch('main.get_db_connection', new_callable=AsyncMock) as mock:
        yield mock


def test_test_endpoint():
    response = client.get("/test")
    assert response.status_code == 200
    assert response.json() == {"message": "POS-сервер работает!"}


@pytest.mark.asyncio
async def test_create_order(mock_db):
    mock_conn = AsyncMock()
    mock_db.return_value = mock_conn

    test_uuid = uuid.uuid4()
    uuid_mock = patch('uuid.uuid4', return_value=test_uuid)
    datetime_test_value = "2023-01-01 00:00:00"
    datetime_mock = patch('datetime.datetime')

    with uuid_mock, datetime_mock as dt_mock:
        dt_mock.now.return_value = datetime_test_value
        response = client.post("/create_order")

    assert response.status_code == 200
    assert response.json() == {"order_id": str(test_uuid)}

    mock_conn.execute.assert_awaited_once()
    mock_conn.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_add_order_items(mock_db):
    mock_conn = AsyncMock()
    mock_db.return_value = mock_conn

    order_uuid = uuid.uuid4()
    item_uuid = uuid.uuid4()
    uuid_mock = patch('uuid.uuid4', return_value=item_uuid)

    order_data = {
        "order_id": str(order_uuid),
        "items": [{"menu_id": str(uuid.uuid4())}, {"menu_id": str(uuid.uuid4())}]
    }

    with uuid_mock:
        response = client.post("/order_item", json=order_data)

    assert response.status_code == 200
    assert response.json() == {"": "Items added successfully!"}

    assert mock_conn.execute.await_count == 2
    mock_conn.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_order_items(mock_db):
    mock_conn = AsyncMock()
    mock_db.return_value = mock_conn

    item_ids = [str(uuid.uuid4()), str(uuid.uuid4())]
    response = client.post("/delete_order_items", json=item_ids)

    assert response.status_code == 200
    assert response.json() == {"": "Delete successfully!"}

    mock_conn.execute.assert_awaited_once()
    mock_conn.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_add_menu_item(mock_db):
    mock_conn = AsyncMock()
    mock_db.return_value = mock_conn

    test_uuid = uuid.uuid4()
    uuid_mock = patch('uuid.uuid4', return_value=test_uuid)

    items = [{"name": "Пицца", "price": 800}, {"name": "Клубничный коктейль", "price": 350}]

    with uuid_mock:
        response = client.post("/add_menu_item", json=items)

    assert response.status_code == 200
    assert response.json() == {"": "New menu items added successfully!"}

    assert mock_conn.execute.await_count == 2
    mock_conn.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_menu_item(mock_db):
    mock_conn = AsyncMock()
    mock_db.return_value = mock_conn

    menu_id = {"menu_id": str(uuid.uuid4())}
    response = client.post("/delete_menu_item", json=menu_id)

    assert response.status_code == 200
    assert response.json() == {"": "Menu item deleted successfully!"}

    mock_conn.execute.assert_awaited_once()
    mock_conn.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_cancel_order(mock_db):
    mock_conn = AsyncMock()
    mock_db.return_value = mock_conn

    order_id = {"order_id": str(uuid.uuid4())}
    response = client.post("/cancel_order", json=order_id)

    assert response.status_code == 200
    assert response.json() == {"": f"Cancel order {order_id['order_id']} successfully!"}

    assert mock_conn.execute.await_count == 2
    mock_conn.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_close_order(mock_db):
    mock_conn = AsyncMock()
    mock_db.return_value = mock_conn

    datetime_mock = patch('datetime.datetime')

    order_data = {
        "order_id": str(uuid.uuid4()),
        "payment_method": "card",
        "tips": 200
    }

    with datetime_mock as dt_mock:
        dt_mock.now.return_value = "2023-01-01 00:00:00"
        response = client.post("/close_order", json=order_data)

    assert response.status_code == 200
    assert response.json() == {"": f"Order {order_data['order_id']} closed"}

    mock_conn.execute.assert_awaited_once_with(
        "UPDATE orders SET status = 'closed', payment_method = $1, tips = $2, closed_at = $3 WHERE order_id = $4",
        "card", 200, "2023-01-01 00:00:00", uuid.UUID(order_data["order_id"])
    )
    mock_conn.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_menu(mock_db):
    mock_conn = AsyncMock()
    mock_db.return_value = mock_conn

    mock_menu = [
        {"menu_id": str(uuid.uuid4()), "name": "Пицца", "price": 800, "is_deleted": False},
        {"menu_id": str(uuid.uuid4()), "name": "Клубничный коктейль", "price": 350, "is_deleted": False}
    ]
    mock_conn.fetch.return_value = mock_menu

    response = client.get("/menu")

    assert response.status_code == 200
    assert response.json() == {"menu": mock_menu}

    mock_conn.fetch.assert_awaited_once_with(
        "SELECT * FROM menu WHERE is_deleted = FALSE"
    )
    mock_conn.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_receipt(mock_db):
    mock_conn = AsyncMock()
    mock_db.return_value = mock_conn

    order_id = str(uuid.uuid4())
    mock_order = [{"order_id": order_id, "status": "closed", "created_at": "2023-01-01 00:00:00"}]
    mock_items = [
        {"order_item_id": str(uuid.uuid4()), "name": "Пицца", "price": 800},
        {"order_item_id": str(uuid.uuid4()), "name": "Клубничный коктейль", "price": 350}
    ]

    mock_conn.fetch.side_effect = [mock_order, mock_items]

    response = client.get(f"/receipt/{order_id}")

    assert response.status_code == 200
    assert response.json() == {
        "order": mock_order,
        "items": mock_items
    }

    assert mock_conn.fetch.await_args_list[0][0][0] == "SELECT * FROM orders WHERE order_id = $1"
    assert mock_conn.fetch.await_args_list[1][0][0] == (
        "SELECT order_item_id, menu.name, menu.price FROM order_items "
        "INNER JOIN menu ON order_items.menu_id = menu.menu_id WHERE order_id = $1"
    )
    mock_conn.close.assert_awaited_once()