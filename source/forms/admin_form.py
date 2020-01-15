from flask_wtf import Form
from wtforms import StringField, SubmitField, HiddenField
from wtforms import validators


class AdminForm(Form):
    id = HiddenField()

    login = StringField("login: ", [
        validators.DataRequired("Please enter admin login."),
        validators.Length(3, 255, "Name should be from 3 to 255 symbols")
    ])

    password = StringField("password: ", [
        validators.DataRequired("Please enter admin password."),
        validators.Length(3, 255, "Name should be from 3 to 255 symbols")
    ])

    submit = SubmitField("Save")

    def strip(self):
        self.login.data = self.login.data.strip()
        self.password.data = self.password.data.strip()
