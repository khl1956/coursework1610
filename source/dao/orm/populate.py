from source.dao.orm.entities import *
from source.dao.db import PostgresDb
import numpy as np
import pandas as pd
import datetime


def populate(path=''):
    db = PostgresDb()
    Base.metadata.create_all(db.sqlalchemy_engine)

    session = db.sqlalchemy_session

    session.query(Training).delete()
    session.query(Plan_exercises).delete()
    session.query(Plan).delete()
    session.query(Exercise).delete()
    session.query(User).delete()
    session.query(Admin).delete()

    adm = Admin(login='admin', password='admin')

    user1 = User(name='user_1', surname='user_1', login='user_1', password='user_1')
    user2 = User(name='user_2', surname='user_2', login='user_2', password='user_2')
    user3 = User(name='user_3', surname='user_3', login='user_3', password='user_3')

    exer_1 = Exercise(title='exer_1', muscle_type='type_1', description='exer_1')
    exer_2 = Exercise(title='exer_2', muscle_type='type_1', description='exer_2')
    exer_3 = Exercise(title='exer_3', muscle_type='type_2', description='exer_3')
    exer_4 = Exercise(title='exer_4', muscle_type='type_2', description='exer_4')

    plan_1 = Plan(title='plan_1', user_created=False)
    plan_2 = Plan(title='plan_2', user_created=False)

    plan_1_1 = Plan_exercises(plan_fk=1, exercise_id=1, weight=20, count=10)
    plan_1_2 = Plan_exercises(plan_fk=1, exercise_id=2, weight=10, count=10)
    plan_1_3 = Plan_exercises(plan_fk=1, exercise_id=3, weight=15, count=10)

    plan_2_1 = Plan_exercises(plan_fk=2, exercise_id=2, weight=15, count=10)
    plan_2_2 = Plan_exercises(plan_fk=2, exercise_id=4, weight=13, count=10)
    plan_2_3 = Plan_exercises(plan_fk=2, exercise_id=3, weight=11, count=10)

    train_1 = Training(user_id=1, plan_id=1, date=datetime.date.today())
    train_2 = Training(user_id=2, plan_id=2, date=datetime.date.today())
    train_3 = Training(user_id=3, plan_id=1, date=datetime.date.today())

    # insert into database
    session.add_all(
        [adm, user1, user2, user3, exer_1, exer_2, exer_3, exer_4, plan_1, plan_2, plan_1_1, plan_1_2, plan_1_3,
         plan_2_1, plan_2_2, plan_2_3, train_1, train_2, train_3])
    session.commit()

    session.add_all([])
    session.commit()


if __name__ == '__main__':
    populate()
