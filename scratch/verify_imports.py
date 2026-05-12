
import sys
from sqlalchemy import __version__
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

print(f"Python path: {sys.executable}")
print(f"SQLAlchemy version: {__version__}")
print("Successfully imported SQLAlchemy and its submodules.")
