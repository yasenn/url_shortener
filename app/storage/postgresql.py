import os
import psycopg2
from psycopg2 import sql

from app.storage.base import URLStorage

from flask import current_app
import time

class PostgreSQLURLStorage(URLStorage):
    def __init__(self):
        self.conn_params = {
            'dbname': os.getenv('POSTGRES_DB'),
            'user': os.getenv('POSTGRES_USER'),
            'password': os.getenv('POSTGRES_PASSWORD'),
            'host': os.getenv('POSTGRES_HOST'),
            'port': os.getenv('POSTGRES_PORT', 5432)
        }
        self._retry_connection()

    def _retry_connection(self, max_retries=5, delay=5):
        for attempt in range(max_retries):
            try:
                self._ensure_tables_exist()
                return
            except psycopg2.OperationalError as e:
                if attempt < max_retries - 1:
                    print(f"Connection attempt {attempt+1} failed. Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    print("Max retries reached. Failed to connect to PostgreSQL.")
                    raise e
                    
    def _get_connection(self):
        return psycopg2.connect(**self.conn_params)

    def _ensure_tables_exist(self):
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS urls (
                        short_code VARCHAR(255) PRIMARY KEY,
                        original_url TEXT NOT NULL,
                        user_id VARCHAR(255) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS clicks (
                        id SERIAL PRIMARY KEY,
                        short_code VARCHAR(255) REFERENCES urls(short_code),
                        timestamp TIMESTAMP NOT NULL,
                        ip_address VARCHAR(45) NOT NULL
                    )
                """)
                conn.commit()
        finally:
            conn.close()

    def save_url(self, short_code, original_url, user_id):
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO urls (short_code, original_url, user_id) VALUES (%s, %s, %s)",
                    (short_code, original_url, user_id)
                )
                conn.commit()
        except psycopg2.IntegrityError:
            conn.rollback()
            raise
        finally:
            conn.close()

    def get_url(self, short_code):
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT original_url FROM urls WHERE short_code = %s",
                    (short_code,)
                )
                result = cur.fetchone()
                return result[0] if result else None
        finally:
            conn.close()

    def code_exists(self, short_code):
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT 1 FROM urls WHERE short_code = %s",
                    (short_code,)
                )
                return cur.fetchone() is not None
        finally:
            conn.close()

    def record_click(self, short_code, click_data):
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO clicks (short_code, timestamp, ip_address) VALUES (%s, %s, %s)",
                    (short_code, click_data['timestamp'], click_data['ip'])
                )
                conn.commit()
        finally:
            conn.close()

    def get_urls_by_user(self, user_id):
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT short_code, original_url FROM urls WHERE user_id = %s",
                    (user_id,)
                )
                user_urls = cur.fetchall()
                
                urls_with_clicks = []
                for code, original in user_urls:
                    cur.execute(
                        "SELECT timestamp, ip_address FROM clicks WHERE short_code = %s",
                        (code,)
                    )
                    clicks = [{'timestamp': ts.isoformat(), 'ip': ip} for ts, ip in cur.fetchall()]
                    urls_with_clicks.append({
                        'short_code': code,
                        'original_url': original,
                        'clicks': clicks
                    })
                return urls_with_clicks
        finally:
            conn.close()

