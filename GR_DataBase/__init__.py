"""
GR_DataBase - Módulo de conexión y consultas a SQL Server
"""

from .connection import DatabaseConnection
from .queries import DatabaseQueries

__all__ = ['DatabaseConnection', 'DatabaseQueries']
