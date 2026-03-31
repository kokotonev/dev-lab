"""
This module serves as the central point for importing all models in the application. 
By importing this module, you ensure that all models are registered with SQLModel's metadata, which is essential for Alembic's autogeneration of migration scripts.
Make sure to import all your models here, so they are included in the metadata and can be detected by Alembic when generating migrations.
"""
from src.models.user import User
