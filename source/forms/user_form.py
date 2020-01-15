from flask_wtf import Form
from wtforms import StringField, SubmitField, HiddenField
from wtforms import validators


class UserForm(Form):
    id = HiddenField()

    name = StringField("name: ", [
        validators.DataRequired("Please enter professor name."),
        validators.Length(3, 255, "Name should be from 3 to 255 symbols")
    ])

    surname = StringField("surname: ", [
        validators.DataRequired("Please enter professor surname."),
        validators.Length(3, 255, "Type should be from 3 to 255 symbols")
    ])

    login = StringField("login: ", [
        validators.DataRequired("Please enter student login."),
        validators.Length(3, 255, "Name should be from 3 to 255 symbols")
    ])

    password = StringField("password: ", [
        validators.DataRequired("Please enter student password."),
        validators.Length(3, 255, "Name should be from 3 to 255 symbols")
    ])

    submit = SubmitField("Save")

    def strip(self):
        self.name.data = self.name.data.strip()
        self.surname.data = self.surname.data.strip()
        self.login.data = self.login.data.strip()
        self.password.data = self.password.data.strip()