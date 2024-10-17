import logging

from flask import render_template, Blueprint, request
from sqlalchemy import select, delete

from backend.server.config import db
from backend.server.models import ExerciseSetDB, WorkoutDB
from backend.server.models.ExerciseDB import CATEGORY_LIST
from backend.server.models.ExerciseDB import ExerciseDB
from backend.server.models.FormFields import CategoryField
from backend.server.routes.database import new_exercise_entries

logger = logging.getLogger(__name__)
admin_bp = Blueprint("admin_bp", __name__, url_prefix="/admin")


def _format_display_exercise_names(values: list | str) -> list[str] | str:
    # applies title formatting
    if isinstance(values, list):
        values = [str(x).replace("_", " ").title() for x in values]
        if "None" in values:
            values.remove("None")
        values = sorted(values)
    elif isinstance(values, str):
        values = str(values).replace("_", " ").title()
    else:
        raise TypeError(f"Values must be a string or list but is {type(values)}")
    return values


def _format_DB_exercise_names(values: list | str) -> list[str] | str:
    # applies the single word & all caps formatting
    if isinstance(values, list):
        values = [str(x).replace(" ", "_").upper() for x in values]
        values = sorted(values)
    elif isinstance(values, str):
        values = str(values).replace(" ", "_").upper()
    else:
        raise TypeError(f"Values must be a string or list but is {type(values)}")
    return values


# obfuscate admin routes w/ pokemon
# clear: clefairy
# record categories for exercises: caterpie
# TODO: remove routes for prod


@admin_bp.route("/clefairy")
def clear_db():
    # Clears out Exercise Info
    delete_sets = delete(ExerciseSetDB)
    delete_workouts = delete(WorkoutDB)
    db.session.execute(delete_sets)
    db.session.execute(delete_workouts)
    db.session.commit()
    return render_template("base.html", body="DB Emptied")


@admin_bp.route("/caterpie", methods=["GET", "POST"])
def record_exercises():
    categories = CATEGORY_LIST
    categorized_exercises = (
        (db.session.execute(select(ExerciseDB.exerciseName))).scalars().all()
    )
    displayed_exercises = _format_display_exercise_names(
        (db.session.execute(select(ExerciseSetDB.exerciseName)))
        .scalars()
        .unique()
        .all()
    )

    compared_exercises = _format_display_exercise_names(categorized_exercises)
    for exercise in compared_exercises:
        if exercise in displayed_exercises:
            displayed_exercises.remove(exercise)
    categories_field = CategoryField()
    categories_field.set_choices(categories)

    if categories_field.is_submitted():
        exercise_entries = list()
        for cur_exercise_name in displayed_exercises:
            cur_selected_category = request.form.get(f"{cur_exercise_name}")
            cur_selected_category = (
                None
                if cur_selected_category == "-- Select a Category --"
                else cur_selected_category
            )
            cur_exercise = ExerciseDB(
                exerciseName=_format_DB_exercise_names(cur_exercise_name),
                category=cur_selected_category,
            )
            if cur_exercise.category is not None:
                exercise_to_remove = _format_display_exercise_names(
                    cur_exercise.exerciseName
                )
                displayed_exercises.remove(exercise_to_remove)
                exercise_entries.append(cur_exercise)
        new_exercise_entries(exercise_entries)

    return render_template(
        "categorize_exercises.html",
        exercises=displayed_exercises,
        categories_field=categories_field,
    )
