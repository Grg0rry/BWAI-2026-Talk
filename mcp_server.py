from fastmcp import FastMCP
import sqlite3

mcp = FastMCP("ShopApp MCP Server")
DB_PATH = "shopapp.db"

def get_db():
    return sqlite3.connect(DB_PATH)

def seed_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id    INTEGER PRIMARY KEY,
            name  TEXT,
            price REAL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id    TEXT PRIMARY KEY,
            name  TEXT,
            email TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    TEXT,
            product_id INTEGER,
            quantity   INTEGER,
            total      REAL
        )
    """)
    if not conn.execute("SELECT 1 FROM products").fetchone():
        conn.executemany("INSERT INTO products VALUES (?, ?, ?)", [
            (1, "Wireless Headphones", 89.00),
            (2, "Sport Watch",        149.00),
            (3, "Backpack",            45.00),
            (4, "Smart Notebook",      34.00),
        ])
    if not conn.execute("SELECT 1 FROM users").fetchone():
        conn.executemany("INSERT INTO users VALUES (?, ?, ?)", [
            ("user_001", "Alice", "alice@example.com"),
            ("user_002", "Bob",   "bob@example.com"),
        ])
    conn.commit()
    conn.close()

seed_db()

# Tools
@mcp.tool()
def search_products(query: str) -> dict:
    """Search for products in the ShopApp catalogue.

    Args:
        query (str): The search term to look for in product names
            (e.g., "headphones", "watch", "backpack").

    Returns:
        dict: A dictionary containing the search results.
            Includes a 'status' key ('success' or 'error').
            If 'success', includes a 'products' key with a list of matching
            products, each containing 'id', 'name', and 'price'.
            If 'error', includes an 'error_message' key.
    """
    conn = get_db()
    rows = conn.execute(
        "SELECT id, name, price FROM products WHERE name LIKE ?",
        (f"%{query}%",)
    ).fetchall()
    conn.close()
    if not rows:
        return {
            "status": "error",
            "error_message": f"No products found for '{query}'"
        }
    return {
        "status": "success",
        "products": [
            {"id": r[0], "name": r[1], "price": r[2]} for r in rows
        ]
    }

@mcp.tool()
def get_user(user_id: str) -> dict:
    """Retrieve a user's profile from ShopApp.

    Args:
        user_id (str): The unique identifier of the user
            (e.g., "user_001", "user_002").

    Returns:
        dict: A dictionary containing the user's profile.
            Includes a 'status' key ('success' or 'error').
            If 'success', includes 'id', 'name', and 'email' keys.
            If 'error', includes an 'error_message' key.
    """
    conn = get_db()
    row = conn.execute(
        "SELECT id, name, email FROM users WHERE id = ?",
        (user_id,)
    ).fetchone()
    conn.close()
    if not row:
        return {
            "status": "error",
            "error_message": f"User '{user_id}' not found"
        }
    return {
        "status": "success",
        "id": row[0],
        "name": row[1],
        "email": row[2]
    }

@mcp.tool()
def place_order(user_id: str, product_id: int, quantity: int) -> dict:
    """Place an order for a product in ShopApp.

    Args:
        user_id (str): The unique identifier of the user placing the order
            (e.g., "user_001").
        product_id (int): The ID of the product to order
            (e.g., 1 for Wireless Headphones).
        quantity (int): The number of units to purchase.

    Returns:
        dict: A dictionary containing the order confirmation.
            Includes a 'status' key ('success' or 'error').
            If 'success', includes 'order_id', 'product', 'quantity', and 'total'.
            If 'error', includes an 'error_message' key.
    """
    conn = get_db()
    product = conn.execute(
        "SELECT id, name, price FROM products WHERE id = ?",
        (product_id,)
    ).fetchone()
    if not product:
        conn.close()
        return {
            "status": "error",
            "error_message": f"Product ID {product_id} not found"
        }
    total = product[2] * quantity
    cursor = conn.execute(
        "INSERT INTO orders (user_id, product_id, quantity, total) VALUES (?, ?, ?, ?)",
        (user_id, product_id, quantity, total)
    )
    conn.commit()
    order_id = cursor.lastrowid
    conn.close()
    return {
        "status": "success",
        "order_id": order_id,
        "product": product[1],
        "quantity": quantity,
        "total": total
    }

# Run server
if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)
