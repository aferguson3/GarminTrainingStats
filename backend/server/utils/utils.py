import logging
from datetime import datetime
from typing import Tuple

import pandas
import pandas as pd
from sqlalchemy import select, update

from backend.server import db, cache
from backend.server.models import ExerciseSetDB, WorkoutDB
from backend.src.dataframe_accessors import get_rep_ranges

logger = logging.getLogger(__name__)


def _get_dataframe_index(workout_ids: list) -> list[Tuple]:
    index_2d: list[Tuple] = []
    workout_ids = list(set(workout_ids))

    for cur_workout_id in workout_ids:
        cur_workout_date = db.session.execute(
            select(WorkoutDB.datetime).where(WorkoutDB.id == int(cur_workout_id))
        ).scalar()
        cur_sets = db.session.execute(
            select(ExerciseSetDB).where(ExerciseSetDB.workout_id == int(cur_workout_id))
        ).all()
        cur_workout_date = (
            datetime.fromisoformat(cur_workout_date).date().strftime("%m/%d/%y")
        )
        for cur_set_number in list(range(1, len(cur_sets) + 1)):
            index_2d.append((cur_workout_date, cur_set_number))

        db.session.execute(  # TODO: only update when empty
            update(ExerciseSetDB)
            .where(ExerciseSetDB.workout_id == int(cur_workout_id))
            .values(date=cur_workout_date)
        )
        db.session.commit()
    return index_2d


@cache.cached(key_prefix="sets_df")
def get_sets_df() -> pandas.DataFrame:
    sets_df = pd.read_sql(
        "select es.* FROM exercise_sets es JOIN workouts w on es.workout_id = w.id where w.category == 'TRACKED'",
        db.session.connection(),
        parse_dates={"startTime": "%H:%M:%S", "date": "%m/%d/%y"},
        params={"category": "TRACKED"},
    )
    index_df = pd.MultiIndex.from_tuples(
        _get_dataframe_index(sets_df["workout_id"]), names=["Dates", "Sets"]
    )
    sets_df.set_index(index_df, inplace=True)
    return sets_df


def format_display_exercise_names(values: list | str) -> list[str] | str:
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


def format_DB_exercise_names(values: list | str) -> list[str] | str:
    if isinstance(values, list):
        values = [str(x).replace(" ", "_").upper() for x in values]
        values = sorted(values)
    elif isinstance(values, str):
        values = str(values).replace(" ", "_").upper()
    else:
        raise TypeError(f"Values must be a string or list but is {type(values)}")
    return values


@cache.cached(key_prefix="exercise_info")
def get_exercise_info(
    exercise_names: list[str], df: pd.DataFrame, exercise_categories: dict
):

    _dict = dict()
    for exercise_name in exercise_names:
        _dict = _dict | {
            exercise_name: {
                "rep_ranges": get_rep_ranges(df, exercise_name),
                "category": (
                    exercise_categories[exercise_name]
                    if exercise_name in exercise_categories
                    else None
                ),
            }
        }
    return _dict
