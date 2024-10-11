import logging

from backend.server.config import db
from backend.server.models.ExerciseSetDB import ExerciseSetDB
from backend.src.models import Workout

logger = logging.getLogger(__name__)


class WorkoutDB(db.Model):
    __tablename__ = "workouts"
    id = db.Column(db.Integer, primary_key=True)
    activityId = db.Column(db.BigInteger)
    category = db.Column(db.String(50))
    datetime = db.Column(db.String(50))
    isIncomplete = db.Column(db.Boolean)
    name = db.Column(db.String(100))
    version = db.Column(db.String(10))
    sets = db.relationship("ExerciseSetDB", backref="workouts", lazy=True)

    def __init__(self, workout: dict):
        if isinstance(workout, dict):
            self.activityId = workout["activityId"]
            self.category = workout["category"]
            self.datetime = workout["datetime"]
            self.isIncomplete = workout["isIncomplete"]
            self.name = workout["name"]
            self.version = workout["version"]
            self.sets = [ExerciseSetDB(_set) for _set in workout["sets"]]

    def __repr__(self):
        return (
            f"{self.name} {self.version} {self.datetime} actID:{self.activityId}, {self.category} isIncomplete:{self.isIncomplete} "
            f"\nsets:{self.sets}"
        )

    def get_dict(self):
        _dict = {
            "activityId": self.activityId,
            "category": self.category,
            "datetime": self.datetime,
            "isIncomplete": self.isIncomplete,
            "name": self.name,
            "sets": [_set.get_dict() for _set in self.sets],
            "version": self.version,
        }
        return _dict

    @staticmethod
    def list_to_workoutsDB(workouts: list[Workout]):
        workoutsDB = []
        for workout in workouts:
            cur_workoutDB = WorkoutDB(workout.asdict())
            workoutsDB.append(cur_workoutDB)
        return workoutsDB


def workoutsDB_to_dict(workouts: list[WorkoutDB]) -> dict:
    all_workouts = [wo.get_dict() for wo in workouts]
    return {"workouts": all_workouts}
