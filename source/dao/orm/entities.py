from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Boolean
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()


class Admin(Base):
    __tablename__ = 'Admin'

    id = Column(Integer, primary_key=True)
    login = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)


class User(Base):
    __tablename__ = 'User'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    surname = Column(String(255), nullable=False)
    login = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)


class Exercise(Base):
    __tablename__ = 'Exercise'

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    muscle_type = Column(String(255), nullable=False)
    description = Column(String(255), nullable=True)


class Plan(Base):
    __tablename__ = 'Plan'

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    user_created = Column(Boolean, nullable=False)

    Plan_exercises = relationship("Plan_exercises")


class Plan_exercises(Base):
    __tablename__ = 'Plan_exercises'

    id = Column(Integer, primary_key=True)
    plan_fk = Column(Integer, ForeignKey('Plan.id'), nullable=False)
    exercise_id = Column(Integer, ForeignKey('Exercise.id'), nullable=False)
    weight = Column(Integer, nullable=False)
    count = Column(Integer, nullable=False)

    plan_entity = relationship("Plan")
    exercise_entity = relationship("Exercise")


class Training(Base):
    __tablename__ = 'Training'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('User.id'))
    plan_id = Column(Integer, ForeignKey('Plan.id'))
    date = Column(Date, nullable=False)

    plan_entity = relationship("Plan")



if __name__ == '__main__':
    from source.dao.db import PostgresDb

    db = PostgresDb()
    a = db.sqlalchemy_session.query(User).all()
    a = db.sqlalchemy_session.query(Plan).all()

    a = db.sqlalchemy_session.query(Plan_exercises).all()

    print(a)
