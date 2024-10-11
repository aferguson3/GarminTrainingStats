from backend.server.config import db


class ExerciseSetDB(db.Model):
    __tablename__ = "exercise_sets"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(50))
    duration_secs = db.Column(db.Float)
    exerciseName = db.Column(db.String(100))
    numReps = db.Column(db.Integer)
    startTime = db.Column(db.String(50))
    stepIndex = db.Column(db.Integer)
    targetReps = db.Column(db.Integer)
    weight = db.Column(db.Float)
    workout_id = db.Column(db.Integer, db.ForeignKey("workouts.id"), nullable=False)

    def __init__(self, _set: dict):
        self.date = _set["date"] if "date" in _set else None
        self.duration_secs = _set["duration_secs"] if "duration_secs" in _set else None
        self.exerciseName = _set["exerciseName"] if "exerciseName" in _set else None
        self.numReps = _set["numReps"] if "numReps" in _set else None
        self.startTime = _set["startTime"] if "startTime" in _set else None
        self.stepIndex = _set["stepIndex"] if "stepIndex" in _set else None
        self.targetReps = _set["targetReps"] if "targetReps" in _set else None
        self.weight = _set["weight"] if "weight" in _set else None

    def __repr__(self):
        return (
            f"exercise:{self.exerciseName}, start:{self.startTime}, reps:{self.numReps}, targetReps:{self.targetReps} "
            f"dur:{self.duration_secs}, weight:{self.weight}, date:{self.date}, stepIndex:{self.stepIndex}, workout_id:{self.workout_id}"
        )

    def get_dict(self):
        _dict = {
            "date": self.date,
            "duration_secs": self.duration_secs,
            "exerciseName": self.exerciseName,
            "numReps": self.numReps,
            "startTime": self.startTime,
            "stepIndex": self.stepIndex,
            "targetReps": self.targetReps,
            "weight": self.weight,
        }
        return _dict
