from flask_wtf import Form
from wtforms import StringField, SubmitField, HiddenField
from wtforms import validators


class ExerciseForm(Form):
    id = HiddenField()

    title = StringField("title: ", [
        validators.DataRequired("Please enter title."),
        validators.Length(3, 255, "Name should be from 3 to 255 symbols")
    ])

    muscle_type = StringField("muscle type: ", [
        validators.DataRequired("Please enter muscle type."),
        validators.Length(3, 255, "Name should be from 3 to 255 symbols")
    ])

    description = StringField("description: ",)

    submit = SubmitField("Save")

    def strip(self):
        self.title.data = self.title.data.strip()
        self.muscle_type.data = self.muscle_type.data.strip()
        self.description.data = self.description.data.strip()

