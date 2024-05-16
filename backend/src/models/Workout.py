import dataclasses
import logging
from dataclasses import dataclass

from backend.src.models.ExerciseSet import ExerciseSet

logger = logging.getLogger(__name__)


@dataclass
class Workout:
    activityId: int
    category: str
    datetime: str
    name: str
    sets: list[ExerciseSet]  # most recent --> oldest
    version: str
    isIncomplete: bool = False

    def __init__(
        self,
        activityId=None,
        category=None,
        datetime=None,
        name=None,
        sets=None,
        version=None,
    ):
        self.activityId = activityId
        self.category = category
        self.datetime = datetime
        self.name = name
        self.sets = sets
        self.version = version

    def asdict(self) -> dict:
        return dataclasses.asdict(self)

    def view_sets(self) -> list[dict]:
        _list = [s.asdict() for s in self.sets]
        return _list

    def transverse_by_set_number(self, targetSet: int) -> list[ExerciseSet]:
        # only returns exercises with the given set number
        setNumber = 1
        matchedStepIndex = self.sets[0].stepIndex
        matchedExercise = self.sets[0].exerciseName
        matchedSets = list()
        for currSet in self.sets:
            if (
                matchedExercise != currSet.exerciseName
                or matchedStepIndex != currSet.stepIndex
            ):
                setNumber = 1
                matchedExercise = currSet.exerciseName
                matchedStepIndex = currSet.stepIndex
            if setNumber == targetSet:
                matchedSets.append(currSet)
            setNumber = setNumber + 1
        return matchedSets

    def list_exercises(self) -> list[str]:
        sets = self.transverse_by_set_number(1)
        exerciseNames = list()
        for currSet in sets:
            exerciseNames.append(currSet.exerciseName)
        ordered_list = list(set(exerciseNames))
        ordered_list.sort(key=lambda x: (x is None, x))
        return ordered_list

    def init_workout(self, data: dict):
        self.activityId = self.key_search(data, "activityId")
        self.category = self.key_search(data, "category")
        self.datetime = self.key_search(data, "datetime")
        self.name = self.key_search(data, "name")
        self.isIncomplete = self.key_search(data, "isIncomplete")
        self.version = self.key_search(data, "version")

        _sets = self.key_search(data, "sets")
        self.sets = [ExerciseSet(loading_dict=s) for s in _sets]

    @staticmethod
    def key_search(data: dict, key_match: str) -> str | bool | list[ExerciseSet] | None:
        # Only finds value of Workout attributes
        for key, value in data.items():
            if key == "sets":
                pass
            if key == key_match:
                return value
            if isinstance(value, dict):
                Workout.key_search(value, key_match)
        return None

    def set_data_validation_check(self):
        # checks if set data is incomplete
        self.isIncomplete = False
        errors = 0
        for currSet in self.sets:
            if currSet.exerciseName is None or currSet.targetReps is None:
                self.isIncomplete = (
                    True  # TODO: cross-reference scheduled workouts and fix errors
                )
                logger.debug(
                    f"FAIL: ID:{self.activityId} date={self.datetime} "
                    f"Exercise={currSet.exerciseName} targetReps={currSet.targetReps} stepIndex={currSet.stepIndex}"
                )
                errors = errors + 1
        if errors > 0:
            logger.debug(f"ID: {self.activityId} date={self.datetime} Errors: {errors}")
