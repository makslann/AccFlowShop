"""SQLite database for AccFlow Shop: products and orders."""

import sqlite3
from pathlib import Path
from typing import Any

DB_PATH = Path(__file__).parent / "accflow.db"


def get_connection() -> sqlite3.Connection:
    """Return a connection to the database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create tables if they do not exist."""
    conn = get_connection()
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                slug TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_slug TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                price REAL NOT NULL,
                FOREIGN KEY (category_slug) REFERENCES categories(slug)
            );

            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (product_id) REFERENCES products(id)
            );
        """)
        conn.commit()

        cur = conn.execute("SELECT COUNT(*) FROM categories")
        if cur.fetchone()[0] == 0:
            conn.executemany(
                "INSERT INTO categories (slug, name) VALUES (?, ?)",
                [("amazon", "Amazon"), ("ebay", "eBay")],
            )
            conn.commit()
    finally:
        conn.close()


def ensure_user(user_id: int, username: str | None = None, first_name: str | None = None) -> None:
    """Insert or ignore user for profile and orders."""
    conn = get_connection()
    try:
        conn.execute(
            """
            INSERT INTO users (user_id, username, first_name)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                username = excluded.username,
                first_name = excluded.first_name
            """,
            (user_id, username or "", first_name or ""),
        )
        conn.commit()
    finally:
        conn.close()


def get_categories() -> list[dict[str, Any]]:
    """Return all categories."""
    conn = get_connection()
    try:
        cur = conn.execute("SELECT id, slug, name FROM categories ORDER BY id")
        return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()


def get_products_by_category(category_slug: str) -> list[dict[str, Any]]:
    """Return products for a category."""
    conn = get_connection()
    try:
        cur = conn.execute(
            "SELECT id, category_slug, name, description, price FROM products WHERE category_slug = ?",
            (category_slug,),
        )
        return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()


def get_product(product_id: int) -> dict[str, Any] | None:
    """Return a single product by id."""
    conn = get_connection()
    try:
        cur = conn.execute(
            "SELECT id, category_slug, name, description, price FROM products WHERE id = ?",
            (product_id,),
        )
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def create_order(user_id: int, product_id: int) -> int:
    """Create order and return its id."""
    conn = get_connection()
    try:
        cur = conn.execute(
            "INSERT INTO orders (user_id, product_id, status) VALUES (?, ?, 'pending')",
            (user_id, product_id),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def get_user_orders(user_id: int) -> list[dict[str, Any]]:
    """Return user's orders with product info."""
    conn = get_connection()
    try:
        cur = conn.execute(
            """
            SELECT o.id, o.product_id, o.status, o.created_at, p.name AS product_name, p.price
            FROM orders o
            JOIN products p ON p.id = o.product_id
            WHERE o.user_id = ?
            ORDER BY o.created_at DESC
            """,
            (user_id,),
        )
        return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()


def add_sample_products() -> None:
    """Add sample products for Amazon and eBay (optional, for testing)."""
    conn = get_connection()
    try:
        cur = conn.execute("SELECT COUNT(*) FROM products")
        if cur.fetchone()[0] > 0:
            return
        conn.executemany(
            """
            INSERT INTO products (category_slug, name, description, price)
            VALUES (?, ?, ?, ?)
            """,
            [
                ("amazon", "Amazon Prime аккаунт", "Полный доступ, проверенный", 299.0),
                ("amazon", "Amazon Seller аккаунт", "Для продавцов", 599.0),
                ("ebay", "eBay аккаунт базовый", "Новый аккаунт", 199.0),
                ("ebay", "eBay аккаунт с историей", "С отзывами", 449.0),
            ],
        )
        conn.commit()
    finally:
        conn.close()
