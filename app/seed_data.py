"""
Seed data for the nutrition management system
"""

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import Base, User, UserRole, Kid, Classroom, Gender, VegPreference
from app.auth import get_password_hash
from datetime import datetime


def create_seed_data():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(User).first():
            print("✅ Seed data already exists!")
            return
        print("🌱 Creating seed data...")
        # Admin
        admin = User(
            username="admin",
            password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
        )
        db.add(admin)
        print("   → Created admin user")
        headmaster = User(
            username="head1",
            password=get_password_hash("pass123"),
            role=UserRole.AUTHORITY,
        )
        db.add(headmaster)
        db.flush()
        classroom1 = Classroom(name="Class 1A", authority_id=headmaster.id)
        db.add(classroom1)
        classroom2 = Classroom(name="Class 2B", authority_id=headmaster.id)
        db.add(classroom2)
        db.flush()
        parents_data = [
            (
                "parent1",
                "pass123",
                "Aarav Kumar",
                "2018-03-15",
                Gender.MALE,
                VegPreference.VEG,
                classroom1.id,
            ),
            (
                "parent2",
                "pass123",
                "Priya Sharma",
                "2017-08-22",
                Gender.FEMALE,
                VegPreference.NON_VEG,
                classroom1.id,
            ),
            (
                "parent3",
                "pass123",
                "Arjun Patel",
                "2019-01-10",
                Gender.MALE,
                VegPreference.VEG,
                classroom2.id,
            ),
            (
                "parent4",
                "pass123",
                "Sneha Gupta",
                "2018-11-05",
                Gender.FEMALE,
                VegPreference.NON_VEG,
                classroom2.id,
            ),
        ]
        for (
            username,
            password,
            kid_name,
            dob,
            gender,
            veg_pref,
            classroom_id,
        ) in parents_data:
            parent = User(
                username=username,
                password=get_password_hash(password),
                role=UserRole.PARENT,
            )
            db.add(parent)
            db.flush()
            kid = Kid(
                name=kid_name,
                date_of_birth=datetime.strptime(dob, "%Y-%m-%d"),
                gender=gender,
                veg_preference=veg_pref,
                parent_id=parent.id,
                classroom_id=classroom_id,
            )
            db.add(kid)
            print(f"   → Created parent {username} and kid {kid_name}")
        db.commit()
        print("✅ Seed data created successfully!")
    except Exception as e:
        print(f"❌ Error creating seed data: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_seed_data()
