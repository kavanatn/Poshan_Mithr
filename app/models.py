"""
SQLAlchemy models for the nutrition management system
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Boolean,
    ForeignKey,
    Text,
    Enum,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class UserRole(enum.Enum):
    ADMIN = "admin"
    AUTHORITY = "authority"
    PARENT = "parent"


class Gender(enum.Enum):
    MALE = "male"
    FEMALE = "female"


class VegPreference(enum.Enum):
    VEG = "veg"
    NON_VEG = "non_veg"


class NutritionStatus(enum.Enum):
    UNDERWEIGHT = "underweight"
    HEALTHY = "healthy"
    OVERWEIGHT = "overweight"
    OBESE = "obese"


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password = Column(String(100), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    created_at = Column(DateTime, default=func.now())
    is_active = Column(Boolean, default=True)
    classrooms = relationship("Classroom", back_populates="authority")
    kids = relationship("Kid", back_populates="parent")


class Kid(Base):
    __tablename__ = "kids"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    date_of_birth = Column(DateTime, nullable=False)
    gender = Column(Enum(Gender), nullable=False)
    veg_preference = Column(Enum(VegPreference), nullable=False)
    parent_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    classroom_id = Column(Integer, ForeignKey("classrooms.id"), nullable=True)
    created_at = Column(DateTime, default=func.now())
    parent = relationship("User", back_populates="kids")
    classroom = relationship("Classroom", back_populates="kids")
    measurements = relationship("Measurement", back_populates="kid")
    nutrition_reports = relationship("NutritionReport", back_populates="kid")


class Classroom(Base):
    __tablename__ = "classrooms"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    authority_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())
    authority = relationship("User", back_populates="classrooms")
    kids = relationship("Kid", back_populates="classroom")


class Measurement(Base):
    __tablename__ = "measurements"
    id = Column(Integer, primary_key=True, index=True)
    kid_id = Column(Integer, ForeignKey("kids.id"), nullable=False)
    height = Column(Float, nullable=False)
    weight = Column(Float, nullable=False)
    measurement_date = Column(DateTime, default=func.now())
    kid = relationship("Kid", back_populates="measurements")


class NutritionReport(Base):
    __tablename__ = "nutrition_reports"
    id = Column(Integer, primary_key=True, index=True)
    kid_id = Column(Integer, ForeignKey("kids.id"), nullable=False)
    bmi = Column(Float, nullable=False)
    bmi_percentile = Column(Float, nullable=True)
    status = Column(Enum(NutritionStatus), nullable=False)
    deficiencies = Column(Text, nullable=True)
    recommendation = Column(Text, nullable=True)
    report_date = Column(DateTime, default=func.now())
    kid = relationship("Kid", back_populates="nutrition_reports")
