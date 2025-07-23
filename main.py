import uuid
import datetime

from fastapi import FastAPI

from models import OrderUpdate, OrderClose, MenuItem
from database import get_db_connection

app = FastAPI()


@app.get("/test")
async def test():
    return {"message": "POS-сервер работает!"}


@app.post("/create_order")
async def create_order():
    conn = await get_db_connection()

    my_uuid = uuid.uuid4()

    await conn.execute(
        "INSERT INTO orders (order_id, status, created_at) VALUES ($1, $2, $3)",
        my_uuid, 'opened', datetime.datetime.now()
    )

    await conn.close()
    return {"order_id": my_uuid}


@app.post("/order_item")
async def add_order_item(order: OrderUpdate):
    conn = await get_db_connection()

    for item in order.items:
        my_uuid = uuid.uuid4()
        await conn.execute(
            "INSERT INTO order_items (order_id, order_item_id, menu_id) VALUES ($1, $2, $3)",
            order.order_id, my_uuid, item.menu_id
        )

    await conn.close()
    return {"order_item_id": my_uuid}


@app.post("/delete_order_item")
async def delete_order_item(order_item_id: uuid.UUID):
    conn = await get_db_connection()

    await conn.execute(
        "DELETE FROM order_items WHERE order_item_id = $1",
        order_item_id
    )

    await conn.close()
    return{"": "Delete successfully!"}


@app.post("/add_menu_item")
async def add_menu_item(item_list: list[MenuItem]):
    conn = await get_db_connection()

    for item in item_list:
        my_uuid = uuid.uuid4()
        await conn.execute(
            "INSERT INTO menu (menu_id, name, price) VALUES ($1, $2, $3)",
            my_uuid, item.name, item.price
        )

    await conn.close()
    return{"": "New menu items added successfully!"}


@app.post("/delete_menu_item")
async def delete_menu_item(menu_id: uuid.UUID):
    conn = await get_db_connection()

    await conn.execute(
        "UPDATE menu SET is_deleted = TRUE WHERE menu_id = $1",
        menu_id
    )

    await conn.close()
    return{"": "Menu item deleted successfully!"}


@app.post("/cancel_order")
async def cancel_order(order_id: uuid.UUID):
    conn = await get_db_connection()

    await conn.execute(
        "DELETE FROM order_items WHERE order_id = $1",
        order_id
    )

    await conn.execute(
        "DELETE FROM orders WHERE order_id = $1",
        order_id
    )

    await conn.close()
    return{"": f"Cancel order {order_id} successfully!"}


@app.post("/close_order")
async def close_order(order: OrderClose):
    conn = await get_db_connection()

    await conn.execute(
        "UPDATE orders SET status = 'closed', payment_method = $1, tips = $2, closed_at = $3 WHERE order_id = $4",
        order.payment_method, order.tips, datetime.datetime.now(), order.order_id
    )

    await conn.close()
    return{"": f"Order {order.order_id} closed"}


@app.get("/menu")
async def get_menu():
    conn = await get_db_connection()

    menu = await conn.fetch(
        "SELECT * FROM menu WHERE is_deleted = FALSE"
    )

    await conn.close()
    return {"menu": menu}


@app.get("/receipt/{order_id}")
async def get_receipt(order_id: uuid.UUID):
    conn = await get_db_connection()

    order = await conn.fetch(
        "SELECT * FROM orders WHERE order_id = $1",
        order_id
    )

    items = await conn.fetch(
        "SELECT order_item_id, menu.name, menu.price FROM order_items INNER JOIN menu ON order_items.menu_id = menu.menu_id WHERE order_id = $1",
        order_id
    )

    await conn.close()
    return {"order": order, "items": items}