import logging

from flask import Blueprint, render_template
from sqlalchemy import select, update

from backend.server import APP_DIRECTORY
from backend.server.config import db, cache
from backend.server.models.MuscleMapDB import MuscleMapDB
from backend.server.models.WorkoutDB import WorkoutDB, workoutsDB_to_dict
from backend.src.WorkoutManagement import WorkoutManagement as Manager
from backend.src.models import Workout
from backend.src.utils import filepath_validation

logger = logging.getLogger(__name__)
database_bp = Blueprint("database_bp", __name__, url_prefix="/db")


def _isNewWorkoutEntry(entry: WorkoutDB) -> bool:
    result = (
        db.session.execute(
            select(WorkoutDB.activityId).where(
                WorkoutDB.activityId is int(entry.activityId)
            )
        )
        .scalars()
        .first()
    )
    return result is None


def _isNewExerciseEntry(entry: MuscleMapDB) -> bool:
    result = (
        db.session.execute(
            select(MuscleMapDB.exerciseName).where(
                MuscleMapDB.exerciseName is str(entry.exerciseName)
            )
        )
        .scalars()
        .first()
    )
    return result is None


def new_workout_entries(workouts: list[Workout]):
    if not isinstance(workouts[0], Workout):
        raise ValueError(f"{type(workouts[0])} is not type Workout")

    cache.delete("sets_df")
    workoutsDB = WorkoutDB.list_to_workoutsDB(workouts)

    for wo in workoutsDB:
        if not _isNewWorkoutEntry(wo) or wo.category == "UNTRACKED":
            continue
        db.session.add(wo)
    db.session.commit()


def new_muscle_maps(values: list[MuscleMapDB]):
    for exercise in values:
        if not _isNewExerciseEntry(exercise):
            continue
        db.session.add(exercise)
    db.session.commit()


def retrieve_muscle_map_entries() -> list[MuscleMapDB]:
    return (
        (db.session.execute(select(MuscleMapDB))).scalars().all()
    )


def set_muscle_categories(values: list[MuscleMapDB]):
    for value in values:
        # noinspection PyTypeChecker
        db.session.execute(
            update(MuscleMapDB)
            .where(MuscleMapDB.exerciseName == value.exerciseName)
            .values(category=f"{value.category}")
        )
    cache.delete("exercise_info")
    db.session.commit()


@database_bp.route("/load")
def initialize_db():
    # purely initializing DB with stored workouts, NOT updating old entries
    app_directory = APP_DIRECTORY.parent
    datefile = app_directory.parent / "src" / "data" / "workout_data.json"
    load_db_from_file(datefile)

    return render_template("base.html", body="Done"), 200


def load_db_from_file(datafile: str):
    filepath_validation(datafile)
    workouts = Manager.load_workouts(str(datafile))
    new_workout_entries(workouts)


@database_bp.route("/workouts/<int:ID>")
def user_by_id(ID: int):
    result = db.get_or_404(WorkoutDB, ID)
    return render_template("base.html", body=f"{result}")


@database_bp.route("/all_workouts")
def full_db():
    workouts = db.session.execute(select(WorkoutDB)).scalars().all()
    workouts_dict = workoutsDB_to_dict(workouts)
    num_workouts = len(workouts_dict["workouts"])
    return render_template("base.html", body=f"# of workouts: {num_workouts}")
