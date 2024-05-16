import logging
import pathlib

from backend.src import show_graph
from backend.src.garmin_interaction import client_auth, run_service
from backend.src.utils import set_params_by_weeks

DATA_FILEPATH = str(pathlib.Path("./data/workout_data_TEST.json").resolve())
# METADATA_FILEPATH = "./data/workout_metadata.json"

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO)


def main():
    client_auth()
    startDate = "2023-01-01"
    weeks_of_workouts = 16

    params = set_params_by_weeks(weeks_of_workouts, startDate)
    menu = (
        "1: Fresh data & backup\n"
        "2: Fresh data & no backup\n"
        "3: Loaded data & no backup\n"
        "Choose an option: "
    )
    while True:
        match input(menu):
            case "1":  # Fresh data & backup
                workouts = run_service(params, backup=True, filepath=DATA_FILEPATH)
                break
            case "2":  # Fresh data & no backup
                workouts = run_service(params)
                break
            case "3":  # Loaded data & no backup
                workouts = run_service(params, load=True, filepath=DATA_FILEPATH)
                break
            case _:
                pass

    while True:
        show_graph(workouts)


if __name__ == "__main__":
    main()
