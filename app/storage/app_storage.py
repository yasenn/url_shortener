from abc import ABC, abstractmethod
import psycopg2
import os
import time

from flask import current_app


class UserStorage(ABC):
    @abstractmethod
    def create_user(self, username, password_hash, role):
        pass
    
    @abstractmethod
    def get_user(self, username):
        pass

class PostgreSQLUserStorage(UserStorage):
    def __init__(self):
        self.conn_params = {
            'dbname': os.getenv('POSTGRES_DB'),
            'user': os.getenv('POSTGRES_USER'),
            'password': os.getenv('POSTGRES_PASSWORD'),
            'host': os.getenv('POSTGRES_HOST'),
            'port': os.getenv('POSTGRES_PORT', 5432)
        }
        self._ensure_table_exists()

    def _get_connection(self):
        return psycopg2.connect(**self.conn_params)

    def _ensure_table_exists(self):
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        username VARCHAR(255) PRIMARY KEY,
                        password_hash TEXT NOT NULL,
                        role VARCHAR(50) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.commit()
        finally:
            conn.close()

    def create_user(self, username, password_hash, role='user'):
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
                    (username, password_hash, role)
                )
                conn.commit()
                return True
        except psycopg2.IntegrityError:  # Duplicate username
            conn.rollback()
            return False
        finally:
            conn.close()

    def get_user(self, username):
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT username, password_hash, role FROM users WHERE username = %s",
                    (username,)
                )
                result = cur.fetchone()
                if result:
                    return {
                        'username': result[0],
                        'password_hash': result[1],
                        'role': result[2]
                    }
                return None
        finally:
            conn.close()