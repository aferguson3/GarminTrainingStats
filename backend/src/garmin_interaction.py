import logging
import multiprocessing
import pathlib
import queue
import re
from datetime import datetime, timedelta
from threading import Thread
from typing import Tuple

import garth
from dotenv import dotenv_values
from garth.exc import GarthHTTPError

from backend.src.WorkoutManagement import WorkoutManagement as Manager
from backend.src.models import Workout, ExerciseSet
from backend.src.utils import Endpoints
from backend.src.utils.utils import timer

logger = logging.getLogger(__name__)
q = queue.Queue()
MAX_THREADS = multiprocessing.cpu_count()
NUM_THREADS = 6
NUM_THREADS = NUM_THREADS if MAX_THREADS >= NUM_THREADS else multiprocessing.cpu_count()


# Assumes Garmin connect user/pass are saved in .env file
def client_auth():
    working_dir = pathlib.Path.cwd().parent.parent
    creds_path = working_dir / "backend" / "creds"
    env_path = working_dir / ".env"
    try:
        garth.resume(str(creds_path))
        logger.info("0Auth tokens found. Login successful.")
    except FileNotFoundError:
        if not pathlib.Path.exists(creds_path):
            pathlib.Path.mkdir(creds_path)
        config = dotenv_values(str(env_path))
        garth.login(config["EMAIL"], config["PASSWORD"])
        garth.save(str(creds_path))


# Gathers all fitness activities by date
def get_activities(params: dict) -> Tuple[list[int], list[str]]:
    activity_data = garth.connectapi(
        f"{Endpoints.garmin_connect_activities}", params=params
    )
    activityIds, removedIds = list(), list()
    activityDatetimes = list()

    for activity in activity_data:
        if (
            str(activity["activityName"]).find("Pickup") > -1
            or str(activity["activityName"]).find("Basketball") > -1
        ):
            # Excludes the basketball activities
            removedIds.append(activity["activityId"])
            continue

        activityIds.append(activity["activityId"])
        activityDatetimes.append(activity["startTimeLocal"])
    logger.debug(
        f"Max limit for Ids: {params['limit']}, Number of Removed Ids: {len(removedIds)}, Number of Ids: {len(activityIds)}"
        f"\n{activityIds[:5]} ..."
    )
    return activityIds, activityDatetimes


def get_workouts(
    activityIds: list, activityDatetimes: list, threading=True
) -> list[Workout]:
    if threading:
        return get_workouts(activityIds, activityDatetimes, list, threading=threading)
    threads = []
    splice = int(len(activityIds) / NUM_THREADS)
    workouts_rv = []

    if len(activityIds) < NUM_THREADS:
        for ID, _datetime in zip(activityIds, activityDatetimes):
            t = Thread(target=_get_workouts, args=(activityDatetimes, ID))
            t.start()
            threads.append(t)
    else:
        for i in range(0, NUM_THREADS):
            cur_index = i * splice
            t = Thread(
                target=_get_workouts,
                args=(
                    activityDatetimes[cur_index : cur_index + splice],
                    activityIds[cur_index : cur_index + splice],
                ),
            )
            t.start()
            threads.append(t)

    for t in threads:
        t.join()
    while not q.empty():
        workouts_rv = workouts_rv + q.get()
    return workouts_rv


def _get_workouts(
    activityDatetimes: list, activityIds: list | int, threading=True
) -> None | list[Workout]:
    totalWorkouts = list()  # most recent workouts stored first
    if isinstance(activityDatetimes, str):
        activityDatetimes = [activityDatetimes]
    if isinstance(activityIds, int):
        activityIds = [activityIds]

    for Id, _datetime in zip(activityIds, activityDatetimes):
        data = garth.connectapi(
            f"{Endpoints.garmin_connect_activity}/{Id}/exerciseSets"
        )
        a_workout = Workout()
        all_workout_sets = list()

        for currSet in data["exerciseSets"]:
            a_set = ExerciseSet()
            if currSet["setType"] == "REST":
                continue
            if currSet["exercises"][0]["category"] == "INDOOR_BIKE":
                continue
            if _isWarmupSet(currSet):
                # skip warmup sets
                logger.debug(
                    f"Skipped {currSet['exercises'][0]['name']}, weight: {currSet['weight']}"
                )
                continue
            currWeight = currSet["weight"] if currSet["weight"] is not None else 0
            curr_time = _format_set_time(currSet["startTime"], timedelta(hours=5))

            a_set.exerciseName = currSet["exercises"][0]["name"]
            a_set.duration_secs = currSet["duration"]
            a_set.numReps = currSet["repetitionCount"]
            a_set.weight = round(currWeight * 0.002204623)
            a_set.startTime = curr_time
            a_set.stepIndex = currSet["wktStepIndex"]
            all_workout_sets.append(a_set)

        a_workout.activityId = Id
        a_workout.datetime = _datetime
        a_workout.sets = all_workout_sets
        totalWorkouts.append(a_workout)
    if threading:
        return totalWorkouts

    q.put(totalWorkouts)
    q.task_done()


def _format_set_time(
    set_time: str | None, timedelta_from_Garmin: timedelta
) -> str | None:
    if set_time is None:
        return
    set_time = set_time.replace(".0", "")
    set_time_dt = datetime.fromisoformat(set_time)
    formatted_time = (set_time_dt - timedelta_from_Garmin).time().isoformat()
    return formatted_time


def _isWarmupSet(garmin_exercise_set: dict) -> bool:
    result = (
        garmin_exercise_set["exercises"][0]["name"] == "BARBELL_BENCH_PRESS"
        and garmin_exercise_set["weight"] <= 61251
    )
    result = (
        result
        or garmin_exercise_set["exercises"][0]["name"] == "BARBELL_BACK_SQUAT"
        and garmin_exercise_set["weight"] <= 61251
    )
    result = (
        result
        or garmin_exercise_set["exercises"][0]["name"] == "BARBELL_DEADLIFT"
        and garmin_exercise_set["weight"] <= 61251
    )
    return result


@timer
def fill_out_workouts(workouts: list[Workout], threading=True) -> list[Workout]:
    # Fills out targetReps and missing exerciseNames using scheduled workout info
    if not threading:
        return _fill_out_workouts(workouts, threading=False)
    threads = []
    splice = int(len(workouts) / NUM_THREADS)
    workouts_rv = []

    if len(workouts) < NUM_THREADS:
        for wo in workouts:
            t = Thread(target=_fill_out_workouts, args=[wo])
            t.start()
            threads.append(t)
    else:
        for i in range(0, NUM_THREADS):
            cur_index = i * splice
            t = Thread(
                target=_fill_out_workouts,
                args=[workouts[cur_index : cur_index + splice]],
            )
            t.start()
            threads.append(t)

    for t in threads:
        t.join()
    while not q.empty():
        workouts_rv = workouts_rv + q.get()

    return workouts_rv


def _fill_out_workouts(
    workouts: list[Workout] | Workout, threading=True
) -> None | list[Workout]:
    if isinstance(workouts, Workout):
        workouts = [workouts]
    workouts_copy = workouts.copy()

    for wo in workouts_copy:
        garmin_data: list = garth.connectapi(
            f"{Endpoints.garmin_connect_activity}/{wo.activityId}/workouts"
        )
        if not garmin_data:  # No planned workout --> remove workout
            workouts.remove(wo)
            continue

        wo_ = _get_workout_name(wo)
        if wo_ is None or wo_.name is None:
            logger.debug(f"Removing ID: {wo.activityId}")
            workouts.remove(wo)
            continue
        else:
            wo = wo_

        garmin_data = garmin_data[0]
        for currSet in wo.sets:
            curr_step_index = currSet.stepIndex
            if curr_step_index is None:
                continue  # Ignores unscheduled exercises w/o stepIndex
            _temp = garmin_data["steps"][curr_step_index]["durationValue"]
            currSet.targetReps = int(_temp) if _temp is not None else None
            if currSet.exerciseName is None:
                new_name = garmin_data["steps"][curr_step_index]["exerciseName"]
                new_category = garmin_data["steps"][curr_step_index]["exerciseCategory"]
                currSet.exerciseName = (
                    new_name if new_name is not None else new_category
                )
    if not threading:
        return workouts
    q.put(workouts)
    q.task_done()


def _get_workout_name(workout: Workout) -> Workout | None:
    pattern = r"\b\d+(?:\.\d+)+\b"
    try:
        garmin_data = garth.connectapi(
            f"{Endpoints.garmin_connect_activity}/{workout.activityId}"
        )
    except GarthHTTPError:
        return

    workout_name_str = garmin_data["activityName"]
    version_str = re.search(pattern, workout_name_str)
    version_str = version_str.group() if version_str is not None else None
    workout_name = re.sub(pattern, "", workout_name_str).strip()

    workout.version = version_str
    workout.name = workout_name
    return workout


def run_service(
    params: dict, backup: bool = False, load: bool = False, filepath: str = None
) -> list[Workout] | None:
    if load is True:
        _filepath_validation(filepath)
        workouts = Manager.load_workouts(filepath)
        workouts_filled = Manager.sort_workouts(workouts, "datetime")
    else:
        IDs, dates = get_activities(params)
        workouts = get_workouts(IDs, dates)
        if len(workouts) == 0:
            return

        workouts_filled = fill_out_workouts(workouts, threading=False)
        workouts_filled = Manager.sort_workouts(workouts_filled, "datetime")
        if backup is True:
            _filepath_validation(filepath)
            Manager.dump_to_json(
                Manager.workouts_to_dict(workouts_filled), filepath, "w"
            )
    Manager.list_incomplete_workouts(workouts_filled)
    logger.info(
        f"Num of workouts: {len(workouts_filled)}, Workout 0: {workouts_filled[0].name} {workouts_filled[0].version}"
        f"\n\tset 3: {workouts_filled[0].view_sets()[3]}"
    )
    return workouts_filled


def _filepath_validation(filepath):
    if type(filepath) is not str:
        raise TypeError(f"{filepath} is invalid filepath.")
