from flask_wtf import FlaskForm
from wtforms import SelectField

from backend.server.models.MuscleMapDB import MUSCLE_GROUPS_LIST


def _pretty_str(name: str):
    return name.replace("_", " ")


class ExerciseMappingForm(FlaskForm):
    categories = SelectField("Categories")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_choices(MUSCLE_GROUPS_LIST)

    def set_choices(self, options: list[str]):
        self.categories.choices = [("", "")] + [(name, name) for name in options]
