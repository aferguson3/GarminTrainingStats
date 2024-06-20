import dataclasses
import json
import logging

from backend.src.models.ExerciseSet import ExerciseSet
from backend.src.models.Workout import Workout

logger = logging.getLogger(__name__)


class WorkoutManagement:
    @staticmethod
    def workouts_to_dict(workouts_list: list[Workout]) -> dict:
        if isinstance(workouts_list, list) is not True:
            raise TypeError(f"{workouts_list} is not type list.")

        workouts = list()
        for workout in workouts_list:
            workouts.append(workout.asdict())
        return {"workouts": workouts}

    @staticmethod
    def set_metadata(workouts_dict: dict, _metadata: dict):
        # Creates metadata from workouts previously sorted by date
        metadata = _metadata.copy()
        try:
            metadata["numWorkouts"] = len(workouts_dict["workouts"])
            metadata["dates"]["firstWorkout"] = workouts_dict["workouts"][0]["datetime"]
            metadata["dates"]["lastWorkout"] = workouts_dict["workouts"][-1]["datetime"]
        except KeyError as k:
            raise KeyError(f"{k}")
        return metadata

    @staticmethod
    def dump_to_json(
        workout_data: dict, filepath: str, option, _metadata: dict | None = None
    ):
        if isinstance(workout_data, dict) is not True:
            raise TypeError(f"{workout_data} is not type dict.")

        match option:
            case "a" | "w":
                try:
                    with open(filepath, option) as file:
                        json.dump(workout_data, file, sort_keys=True)
                except FileNotFoundError:
                    logger.error(f"{filepath} not found.")
                    raise FileNotFoundError(f"{filepath} not found")

            case _:
                raise ValueError(f"Invalid option:{option} used in json.dump().")

        if _metadata is None:
            return

        logger.info("Metadata enabled.")
        try:
            metadata = WorkoutManagement.set_metadata(workout_data, _metadata)
            filepath = metadata.pop("filepath")
            with open(filepath, "w") as file:
                json.dump(metadata, file)
        except FileNotFoundError:
            logger.error(f"{filepath} not found.")
            raise FileNotFoundError(f"{filepath} not found")

    @staticmethod
    def load_workouts(filepath: str) -> list[Workout]:
        try:
            with open(filepath, "r") as file:
                json_data = json.load(file)
                all_workouts = list()
                for workout in json_data["workouts"]:
                    a_workout = Workout()
                    a_workout.init_workout(workout)
                    all_workouts.append(a_workout)
            return all_workouts

        except FileNotFoundError as e:
            logger.error(f"{e}")
            raise FileNotFoundError(f"{e}")

    @staticmethod
    def sort_workouts(
        workout_data: list[Workout] | Workout, key: str, reverse=False
    ) -> list[Workout] | list[ExerciseSet] | None:
        # Can sort list[Workout] w/ workout keys or Workout w/ ExerciseSet keys
        searchedData, isValidKey = None, None
        if isinstance(workout_data, list):
            if len(workout_data) == 0:
                return
            isValidKey = hasattr(workout_data[0], key)
            searchedData = workout_data
        elif isinstance(workout_data, Workout):
            isValidKey = hasattr(workout_data.sets[0], key)
            searchedData = workout_data.sets

        if isValidKey:
            try:
                sorted_list = sorted(
                    searchedData, key=lambda w: getattr(w, key), reverse=reverse
                )
                return sorted_list
            except TypeError as msg:
                logger.error(f"{msg}")
                raise TypeError(f"{msg}")

        else:
            logger.error(f"Sorting {type(workout_data)} by key: {key} FAILED.")

    @staticmethod
    def view_sets_from_workouts(workout_data: list[Workout]) -> dict:
        # Returns dict of all workouts sets
        if isinstance(workout_data, list) is not True:
            raise TypeError(f"{workout_data} is not type list.")

        _dict = dict()
        for field in dataclasses.fields(ExerciseSet):
            field_data = [
                getattr(_set, field.name) for wo in workout_data for _set in wo.sets
            ]
            _dict[str(field.name)] = field_data

        return _dict

    @staticmethod
    def list_incomplete_workouts(workouts: list[Workout]):
        incomplete_workouts = []
        versionless_workouts = []
        untracked_workouts = []
        for wo in workouts:
            wo.set_data_validation_check()
            cur_date = ""
            if "T" in wo.datetime:
                cur_date = wo.datetime.split("T")[0]
            elif " " in wo.datetime:
                cur_date = wo.datetime.split(" ")[0]

            if wo.isIncomplete or wo.name is None:
                incomplete_workouts.append(cur_date)
            if wo.version is None:
                versionless_workouts.append(cur_date)
            if wo.category == "UNTRACKED":
                untracked_workouts.append(cur_date)

        logger.info(
            f"{len(incomplete_workouts)} Incomplete workouts: {incomplete_workouts}"
        )
        logger.info(
            f"{len(versionless_workouts)} Version-less workouts: {versionless_workouts}"
        )
        logger.info(
            f"{len(untracked_workouts)} Untracked workouts: {untracked_workouts}"
        )
