import logging

from flask import render_template, Blueprint, request
from sqlalchemy import select

from backend.server import db
from backend.server.models import ExerciseSetDB
from backend.server.models.ExerciseDB import ExerciseDB
from backend.server.models.FormFields import CategoryField
from backend.server.routes.database import new_exercise_entries
from backend.server.utils.utils import (
    format_display_exercise_names,
    format_DB_exercise_names,
)

logger = logging.getLogger(__name__)
admin_bp = Blueprint("admin_bp", __name__, url_prefix="/admin")


# obfuscate admin routes w/ pokemon
# clear: clefairy
# recored exercises: caterpie


@admin_bp.route("/clefairy")
def clear_db():
    db.drop_all()
    return render_template("base.html", body="DB Emptied")


@admin_bp.route("/caterpie", methods=["GET", "POST"])
def record_exercises():
    categorized_exercises = (
        (db.session.execute(select(ExerciseDB.exerciseName))).scalars().all()
    )
    displayed_exercises = format_display_exercise_names(
        (db.session.execute(select(ExerciseSetDB.exerciseName)))
        .scalars()
        .unique()
        .all()
    )

    compared_exercises = format_display_exercise_names(categorized_exercises)
    for exercise in compared_exercises:
        if exercise in displayed_exercises:
            displayed_exercises.remove(exercise)
    categories_field = CategoryField()

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
                exerciseName=format_DB_exercise_names(cur_exercise_name),
                category=cur_selected_category,
            )
            if cur_exercise.category is not None:
                exercise_to_remove = format_display_exercise_names(
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
