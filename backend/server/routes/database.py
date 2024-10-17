import logging

from flask import Blueprint, render_template
from sqlalchemy import select

from backend.server import APP_DIRECTORY
from backend.server.config import db, cache
from backend.server.models.ExerciseDB import ExerciseDB
from backend.server.models.WorkoutDB import WorkoutDB, workoutsDB_to_dict
from backend.src.WorkoutManagement import WorkoutManagement as Manager
from backend.src.models import Workout

logger = logging.getLogger(__name__)
database_bp = Blueprint("database_bp", __name__, url_prefix="/db")


def _isNewWorkoutEntry(entry: WorkoutDB) -> bool:
    result = (
        db.session.execute(
            select(WorkoutDB.activityId).where(
                WorkoutDB.activityId == int(entry.activityId)
            )
        )
        .scalars()
        .first()
    )
    return result is None


def _isNewExerciseEntry(entry: ExerciseDB) -> bool:
    result = (
        db.session.execute(
            select(ExerciseDB.exerciseName).where(
                ExerciseDB.exerciseName == str(entry.exerciseName)
            )
        )
        .scalars()
        .first()
    )
    return result is None


def new_workout_entries(workouts: list[Workout]):
    if not isinstance(workouts[0], Workout):
        raise ValueError(f"{type(workouts[0])} is not type Workout")

    cache.delete("get_sets_df")
    workoutsDB = WorkoutDB.list_to_workoutsDB(workouts)

    for wo in workoutsDB:
        if not _isNewWorkoutEntry(wo) or wo.category == "UNTRACKED":
            continue
        db.session.add(wo)
    db.session.commit()


def new_exercise_entries(values: list[ExerciseDB]):
    for exercise in values:
        if not _isNewExerciseEntry(exercise):
            continue
        db.session.add(exercise)
    db.session.commit()


@database_bp.route("/load")
def initialize_db():
    # purely initializing DB with stored workouts, NOT updating old entries
    app_directory = APP_DIRECTORY.parent
    Datafile = app_directory.parent / "src" / "data" / "workout_data.json"
    workouts = Manager.load_workouts(str(Datafile))
    new_workout_entries(workouts)

    return render_template("base.html", body="Done"), 200


@database_bp.route("/workouts/<int:ID>")
def user_by_id(ID):
    result = db.get_or_404(WorkoutDB, ID)
    return render_template("base.html", body=f"{result}")


@database_bp.route("/all_workouts")
def full_db():
    workouts = db.session.execute(select(WorkoutDB)).scalars().all()
    workouts_dict = workoutsDB_to_dict(workouts)
    num_workouts = len(workouts_dict["workouts"])
    return render_template("base.html", body=f"# of workouts: {num_workouts}")
