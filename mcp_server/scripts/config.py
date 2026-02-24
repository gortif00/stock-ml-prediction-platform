"""Módulo de configuración de base de datos.

Gestiona conexiones a PostgreSQL usando un pool thread-safe para
mejorar la concurrencia y evitar conexiones cacheadas cerradas.
"""

import os
import threading
import psycopg2
from psycopg2 import extensions
from psycopg2.extras import RealDictCursor
from psycopg2.pool import ThreadedConnectionPool
from dotenv import load_dotenv

# Variables de entorno para conexión a PostgreSQL
# Valores por defecto apuntan al contenedor Docker
load_dotenv()
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = int(os.getenv("DB_PORT", 5432))
DB_NAME = os.getenv("DB_NAME", "indices")
DB_USER = os.getenv("DB_USER", "finanzas")
DB_PASS = os.getenv("DB_PASS", "finanzas_pass")

# Tamaño del pool de conexiones
DB_POOL_MIN = int(os.getenv("DB_POOL_MIN", 1))
DB_POOL_MAX = int(os.getenv("DB_POOL_MAX", 5))

_pool = None
_pool_lock = threading.Lock()


def _get_pool() -> ThreadedConnectionPool:
    """Inicializa el pool de conexiones de forma segura."""
    global _pool
    if _pool is None:
        with _pool_lock:
            if _pool is None:
                _pool = ThreadedConnectionPool(
                    minconn=DB_POOL_MIN,
                    maxconn=DB_POOL_MAX,
                    host=DB_HOST,
                    port=DB_PORT,
                    dbname=DB_NAME,
                    user=DB_USER,
                    password=DB_PASS,
                    cursor_factory=RealDictCursor,
                )
    return _pool


class _PooledConnection:
    """Wrapper para devolver conexiones al pool al cerrar."""

    def __init__(self, pool: ThreadedConnectionPool, conn: psycopg2.extensions.connection):
        self._pool = pool
        self._conn = conn
        self._released = False

    def __getattr__(self, name):
        return getattr(self._conn, name)

    def close(self):
        if self._released:
            return

        try:
            if self._conn is not None and self._conn.closed == 0:
                # Si hay una transacción abierta, hacemos rollback para dejar la conexión limpia
                if self._conn.get_transaction_status() != extensions.TRANSACTION_STATUS_IDLE:
                    self._conn.rollback()
            self._pool.putconn(self._conn, close=self._conn.closed != 0)
        finally:
            self._released = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()


def get_db_conn():
    """Obtiene una conexión a PostgreSQL desde el pool.

    Returns:
        _PooledConnection: Conexión envuelta que al cerrar vuelve al pool
    """
    pool = _get_pool()
    conn = pool.getconn()
    return _PooledConnection(pool, conn)


def close_db_pool() -> None:
    """Cierra todas las conexiones del pool (uso en shutdown)."""
    global _pool
    if _pool is not None:
        _pool.closeall()
        _pool = None
