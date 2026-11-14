from sqlalchemy import Integer, String, Column, create_engine, ForeignKey
from sqlalchemy.orm import declarative_base, Session
from sqlalchemy.exc import IntegrityError
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from datetime import datetime


DB_PATH = "recruitment.db"
engine = create_engine(f"sqlite:///{DB_PATH}")
Base = declarative_base()


# Database Models

class Clubs(Base):
    __tablename__ = "clubs"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    category = Column(String)
    seats = Column(Integer)
    deadline = Column(String)
    recruiting = Column(Integer)


class Applications(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True)
    club_id = Column(Integer, ForeignKey("clubs.id"))
    roll_no = Column(Integer)
    why_join = Column(String)
    status = Column(String)
    applied_on = Column(String)


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password = Column(String)
    role = Column(String)


Base.metadata.create_all(engine)


# Password Hashing

ph = PasswordHasher()


def hash_password(password):
    return ph.hash(password)


def verify_password(password, hashed_password):
    return ph.verify(hashed_password, password)


# E1 - Get All Clubs

def get_all_clubs(category=None):
    session = Session(engine)

    try:
        if category is None:
            clubs = session.query(Clubs).all()
        else:
            clubs = session.query(Clubs).filter(
                Clubs.category == category
            ).all()

        response = []

        for club in clubs:
            application_count = session.query(Applications).filter(
                Applications.club_id == club.id,
                Applications.status != "withdrawn"
            ).count()

            temp_club = {
                "id": club.id,
                "name": club.name,
                "category": club.category,
                "seats": club.seats,
                "deadline": club.deadline,
                "recruiting": club.recruiting,
                "application_count": application_count
            }

            response.append(temp_club)

        return response

    finally:
        session.close()


# E2 - Get Club By ID

def get_club(id):
    session = Session(engine)

    try:
        club = session.query(Clubs).filter(
            Clubs.id == id
        ).first()

        if club is None:
            return None

        applications = session.query(Applications).filter(
            Applications.club_id == id
        ).all()

        response = {
            "id": club.id,
            "name": club.name,
            "applications": []
        }

        for application in applications:
            response["applications"].append({
                "roll_no": application.roll_no,
                "why_join": application.why_join,
                "status": application.status
            })

        return response

    finally:
        session.close()


# E3 - Add Club

def add_club(name, category, seats, deadline):
    session = Session(engine)

    try:
        club = Clubs(
            name=name,
            category=category,
            seats=seats,
            deadline=deadline,
            recruiting=1
        )

        session.add(club)
        session.commit()
        session.refresh(club)

        response = {
            "id": club.id,
            "name": club.name,
            "category": club.category,
            "seats": club.seats,
            "deadline": club.deadline,
            "recruiting": club.recruiting
        }

        return response

    finally:
        session.close()


# Set Recruiting Status

def set_recruiting(id, recruiting):
    session = Session(engine)

    try:
        club = session.query(Clubs).filter(
            Clubs.id == id
        ).first()

        if club is None:
            return None

        club.recruiting = int(recruiting)
        session.commit()

        response = {
            "id": club.id,
            "name": club.name,
            "recruiting": club.recruiting
        }

        return response

    finally:
        session.close()


# E4 - Apply To Club

def apply_to_club(club_id, roll_no, why_join):
    session = Session(engine)

    try:
        application = Applications(
            club_id=club_id,
            roll_no=roll_no,
            why_join=why_join,
            status="applied",
            applied_on=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

        session.add(application)
        session.commit()
        session.refresh(application)

        response = {
            "id": application.id,
            "club_id": application.club_id,
            "roll_no": application.roll_no,
            "why_join": application.why_join,
            "status": application.status,
            "applied_on": application.applied_on
        }

        return response

    finally:
        session.close()


# E5 - Update Application Status

def update_application_status(id, status):
    session = Session(engine)

    try:
        application = session.query(Applications).filter(
            Applications.id == id
        ).first()

        if application is None:
            return None

        application.status = status
        session.commit()

        response = {
            "id": application.id,
            "club_id": application.club_id,
            "roll_no": application.roll_no,
            "status": application.status
        }

        return response

    finally:
        session.close()


# E6 - Withdraw Application

def withdraw_application(id, roll_no):
    session = Session(engine)

    try:
        application = session.query(Applications).filter(
            Applications.id == id
        ).first()

        if application is None:
            return None

        if application.roll_no != roll_no:
            return "forbidden"

        if application.status != "applied":
            return "not_allowed"

        application.status = "withdrawn"
        session.commit()

        response = {
            "id": application.id,
            "club_id": application.club_id,
            "roll_no": application.roll_no,
            "status": application.status
        }

        return response

    finally:
        session.close()


# E7 - Get Student Applications

def get_student_applications(roll_no):
    session = Session(engine)

    try:
        applications = session.query(Applications).filter(
            Applications.roll_no == roll_no
        ).all()

        response = []

        for application in applications:
            club = session.query(Clubs).filter(
                Clubs.id == application.club_id
            ).first()

            temp_application = {
                "id": application.id,
                "club_id": application.club_id,
                "club_name": club.name if club else None,
                "roll_no": application.roll_no,
                "why_join": application.why_join,
                "status": application.status,
                "applied_on": application.applied_on
            }

            response.append(temp_application)

        return response

    finally:
        session.close()


# E8 - Get Summary

def get_summary():
    session = Session(engine)

    try:
        clubs = session.query(Clubs).all()

        response = []

        for club in clubs:
            temp_club = {
                "club_id": club.id,
                "club_name": club.name,

                "applied": session.query(Applications).filter(
                    Applications.club_id == club.id,
                    Applications.status == "applied"
                ).count(),

                "shortlisted": session.query(Applications).filter(
                    Applications.club_id == club.id,
                    Applications.status == "shortlisted"
                ).count(),

                "selected": session.query(Applications).filter(
                    Applications.club_id == club.id,
                    Applications.status == "selected"
                ).count(),

                "rejected": session.query(Applications).filter(
                    Applications.club_id == club.id,
                    Applications.status == "rejected"
                ).count()
            }

            response.append(temp_club)

        return response

    finally:
        session.close()


# Register User

def register_user(username, password, role):
    session = Session(engine)

    try:
        existing_user = session.query(Users).filter(
            Users.username == username
        ).first()

        if existing_user:
            return None

        user = Users(
            username=username,
            password=hash_password(password),
            role=role
        )

        session.add(user)
        session.commit()
        session.refresh(user)

        response = {
            "id": user.id,
            "username": user.username,
            "role": user.role
        }

        return response

    except IntegrityError:
        session.rollback()
        return None

    finally:
        session.close()


# Login User

def login_user(username, password):
    session = Session(engine)

    try:
        user = session.query(Users).filter(
            Users.username == username
        ).first()

        if user is None:
            return None

        try:
            verify_password(password, user.password)

        except VerifyMismatchError:
            return None

        response = {
            "id": user.id,
            "username": user.username,
            "role": user.role
        }

        return response

    finally:
        session.close()