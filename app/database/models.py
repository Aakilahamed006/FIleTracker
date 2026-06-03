from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey
)
from app.database.db import Base


class FileInitiation(Base):
    __tablename__ = "file_initiation_table"

    id = Column(Integer, primary_key=True, autoincrement=True)

    file_extension = Column(String(50))

    file_name = Column(
        String(255),
        nullable=False
    )

    file_operation = Column(
        String(50),
        nullable=False
    )

    timestamp = Column(
        DateTime,
        nullable=False
    )

    is_operated = Column(
        Boolean,
        default=False
    )

    file_path = Column(
        String,
        nullable=False,
        index=True
    )


class FileLifeCycle(Base):
    __tablename__ = "file_life_cycle"

    id = Column(Integer, primary_key=True, autoincrement=True)

    file_id = Column(
        Integer,
        ForeignKey("file_initiation_table.id"),
        nullable=False
    )

    file_operation = Column(
        String(50),
        nullable=False
    )

    current_location = Column(
        String,
        nullable=False,
        index=True
    )

    current_name = Column(
        String(255),
        nullable=False
    )

    timestamp = Column(
        DateTime,
        nullable=False
    )


