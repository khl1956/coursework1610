from flask_wtf import Form
from wtforms import SelectField, SubmitField, DateField, HiddenField, IntegerField
from datetime import date
from wtforms import validators
from source.dao.db import PostgresDb
import source.dao.orm.entities as entities


class TrainingForm(Form):
    id = HiddenField()

    new_plan_name = HiddenField()

    plan_id = SelectField("Plan based on:", coerce=int)

    date = DateField("date of training: ", [validators.DataRequired("Please enter date ")], default=date.today())

    submit = SubmitField("Save")

    def __init__(self, user_id=0, edit=False, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

        db = PostgresDb()

        user = db.sqlalchemy_session.query(entities.User).filter(entities.User.id == user_id).one()
        plans = db.sqlalchemy_session.query(entities.Plan).all()
        if edit:
            self.plan_id.choices = [(plan.id, "id: '{}'; title: '{}'".format(plan.id, plan.title)) for plan in plans
                                    if plan.user_created and plan.title[:len(user.login)] == user.login]

        else:
            self.plan_id.choices = [(plan.id, "id: '{}'; title: '{}'".format(plan.id, plan.title)) for plan in plans
                                    if (plan.user_created and plan.title[:len(user.login)] == user.login) or (
                                        not plan.user_created)]
