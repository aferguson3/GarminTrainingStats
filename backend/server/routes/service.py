import io
import logging
import pathlib
from datetime import datetime

from flask import (
    Blueprint,
    request,
    render_template,
    session,
    redirect,
    url_for,
)
from sqlalchemy import select

from backend.server import db
from backend.server.models import WorkoutDB
from backend.server.models.ExerciseDB import ExerciseDB
from backend.server.models.FormFields import CategoryField
from backend.server.routes.database import new_workout_entries
from backend.server.utils import get_sets_df
from backend.server.utils.utils import get_exercise_info
from backend.src.dataframe_accessors import (
    list_available_exercises,
    plot_dataframe,
)
from backend.src.garmin_interaction import run_service
from backend.src.utils import set_params_by_weeks
from backend.src.utils import timer

GRAPH_FILE = pathlib.Path.cwd() / "templates" / "plotly_graph_data.html"

logger = logging.getLogger(__name__)
service_bp = Blueprint(
    "service_bp", __name__, url_prefix="/main", template_folder="templates"
)


# Uploads new workout entries
# URL Args: startDate (YYYY-MM-DD), weeks
@service_bp.route("/run", methods=["GET"])
@timer
def service():
    args = request.args
    weeks_of_workouts = args.get("weeks", default=10, type=int)
    start_date = args.get(
        "startDate", default=None, type=str
    )  # provide start date or use the first date in DB

    if start_date is None:
        result = (
            db.session.execute(
                select(WorkoutDB.datetime).order_by(WorkoutDB.datetime.desc())
            )
            .scalars()
            .first()
        )
        if result is None:  # no start date provided and empty DB
            logger.info(ValueError("DB is empty. Please select a start date."))
            return render_template(
                "base.html", body=f"startDate: {start_date}, weeks: {weeks_of_workouts}"
            )
        start_date = datetime.fromisoformat(result).date()
        logger.info(f"startDate: {start_date}, weeks: {weeks_of_workouts}")

    params = set_params_by_weeks(
        weeks_of_workouts=weeks_of_workouts, start_date=start_date
    )
    logger.info(params.items())
    workouts = run_service(params)
    if workouts is not None:
        new_workout_entries(workouts)
    else:
        logger.info(f"No new workout entries.")

    return render_template(
        "base.html", body=f"startDate: {start_date}, weeks: {weeks_of_workouts}"
    )


@service_bp.route("/graph", methods=["GET", "POST"])
def setup_graph():
    df = get_sets_df()
    buffer = io.StringIO()
    df.info(memory_usage=True, buf=buffer)
    logger.info(f"df memory usage: {buffer.getvalue()}")

    categories_field = CategoryField()
    exerciseDB_entries: list[ExerciseDB] = (
        (db.session.execute(select(ExerciseDB))).scalars().all()
    )
    exercise_categories = {
        _dict["exerciseName"]: _dict["category"]
        for _dict in [
            exercise_entry.get_dict() for exercise_entry in exerciseDB_entries
        ]
    }
    all_exercise_names = list_available_exercises(df)
    exercise_info = get_exercise_info(all_exercise_names, df, exercise_categories)

    if categories_field.is_submitted():
        if any(
            request.form.get(val) == ""
            for val in ["categories", "exercises", "rep_ranges"]
        ):
            logger.debug("Submission prevented -- null graph param(s)")
        else:
            session["exercise"] = request.form.get("exercises")
            session["reps"] = request.form.get("rep_ranges")
            return redirect(url_for(".show_graph"))

    return render_template(
        "graph_params.html",
        categories_field=categories_field,
        exercise_info=exercise_info,
    )


@service_bp.route("/graph/show", methods=["GET"])
def show_graph():
    exercise = session["exercise"]
    reps = float(session["reps"]) if session["reps"] != "None" else None
    plot_dataframe(
        get_sets_df(), exercise, reps, flask_mode=True, filepath=str(GRAPH_FILE)
    )
    return render_template(GRAPH_FILE.name)
