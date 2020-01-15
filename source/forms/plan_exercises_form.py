from flask_wtf import Form
from wtforms import SelectField, SubmitField, DateField, HiddenField, IntegerField
from datetime import date
from wtforms import validators
from wtforms.validators import NumberRange
from source.dao.db import PostgresDb
import source.dao.orm.entities as entities


class PlanExercisesForm(Form):
    id = HiddenField()

    plan_fk = SelectField("Plan:", coerce=int)

    exercise_id = SelectField("Exercise:", coerce=int)

    weight = IntegerField("weight for exercise (kg): ", [
        validators.DataRequired("Please enter weight for exercise"),
        NumberRange(min=0, max=300, message='number range between 0 and 300')], default=0)

    count = IntegerField("count of approaches for exercise: ", [
        validators.DataRequired("Please enter count of approaches"),
        NumberRange(min=0, max=20, message='number range between 0 and 20')], default=0)

    submit = SubmitField("Save")

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

        db = PostgresDb()
        plans = db.sqlalchemy_session.query(entities.Plan).all()
        exercises = db.sqlalchemy_session.query(entities.Exercise).all()

        self.plan_fk.choices = [(plan.id, "id: '{}'; title: '{}'".format(plan.id, plan.title)) for plan in plans]

        self.exercise_id.choices = [(exercise.id,
                                     "title: '{}'; muscle_type: '{}'; description: '{}'".format(exercise.title,
                                                                                                exercise.muscle_type,
                                                                                                exercise.description))
                                    for exercise in exercises]
