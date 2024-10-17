import logging
from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
from matplotlib import pyplot as plt
from plotly.io import write_json
from plotly.subplots import make_subplots

from backend.src.WorkoutManagement import WorkoutManagement as Manager
from backend.src.models import Workout
from backend.src.utils import filepath_validation

logger = logging.getLogger(__name__)


def list_available_exercises(dataframe: pd.DataFrame) -> list:
    values = dataframe["exerciseName"].drop_duplicates().values.tolist()
    if None in values:
        values.remove(None)
    return sorted(values)


def load_dataframe(workouts: list[Workout]) -> pd.DataFrame:
    index_2d = []
    for workout in workouts:
        set_numbers = list(range(1, len(workout.sets) + 1))
        workoutDate = (
            datetime.fromisoformat(workout.datetime).date().strftime("%m/%d/%y")
        )
        for cur_set_number in set_numbers:
            index_2d.append((workoutDate, cur_set_number))
    setsData = Manager.view_sets_from_workouts(workouts)
    index_df = pd.MultiIndex.from_tuples(index_2d, names=["Dates", "Sets"])

    df = pd.DataFrame(setsData, index=index_df)
    df["date"] = [_date for (_date, s) in index_2d]
    df["date"] = pd.to_datetime(df["date"], format="%m/%d/%y")
    return df


def plot_dataframe(
    df: pd.DataFrame,
    plotting_exercise: str,
    targetReps: int = None,
    flask_mode: bool = False,
    filepath: str = None,
) -> None:
    # plot the reps and weight of like exercisesNames
    if plotting_exercise not in df["exerciseName"].values:
        raise ValueError(f"Exercise {plotting_exercise} is not in df")

    df["date_str"] = df["date"].dt.strftime("%m/%d/%y")
    df.sort_values(by=["date", "startTime"], inplace=True)
    df.drop_duplicates(
        subset=["date", "exerciseName"], inplace=True
    )  # Gets 1st rep of chosen exercise
    df = df.bfill()

    if targetReps is None:
        plot_df = df.loc[df["exerciseName"] == plotting_exercise]
    else:
        plot_df = df.loc[
            (df["exerciseName"] == plotting_exercise) & (df["targetReps"] == targetReps)
        ]

    if flask_mode is False:
        fig, axes = plt.subplots(2, 1, sharex=True)
        _setup_plot_formatting(plot_df, plotting_exercise, flask_mode, axes=axes)
        plt.show()
    else:
        fig = make_subplots(2, 1, shared_xaxes=True)
        filepath_validation(filepath)
        _setup_plot_formatting(plot_df, plotting_exercise, flask_mode, fig=fig)
        # write_html(fig, file=filepath)
        write_json(fig, file=filepath, pretty=True)


def _setup_plot_formatting(
    plot_df: pd.DataFrame, plotting_exercise: str, flask_mode: bool, axes=None, fig=None
) -> None:
    if flask_mode is False:
        axes[0].set_title(f"{plotting_exercise.replace('_', ' ').title()} Progress")
        datapoints = len(plot_df)
        figsize = (datapoints, 6)

        plot_df.plot(
            x="date_str",
            y=["weight"],
            kind="line",
            ax=axes[0],
            ylabel="Weight (lbs)",
            grid=True,
        )
        plot_df.plot(
            x="date_str",
            y=["targetReps", "numReps"],
            kind="line",
            ax=axes[1],
            xlabel="Dates",
            ylabel="Reps",
            grid=True,
            xticks=range(datapoints),
            rot=30.0,
            figsize=figsize,
        )
    else:
        fig.update_layout(
            title_text=f"{plotting_exercise.replace('_', ' ').title()} Progress",
            xaxis=dict(title="Dates"),
            yaxis=dict(title="Reps"),
        )
        fig.add_traces(
            [
                go.Scatter(
                    x=plot_df["date_str"],
                    y=plot_df["weight"],
                    mode="lines+markers",
                    name="Weight (lbs)",
                ),
                go.Scatter(
                    x=plot_df["date_str"],
                    y=plot_df["targetReps"],
                    mode="lines+markers",
                    name="Target Reps",
                ),
                go.Scatter(
                    x=plot_df["date_str"],
                    y=plot_df["numReps"],
                    mode="lines+markers",
                    name="Reps",
                ),
            ],
            rows=[1, 2, 2],
            cols=[1, 1, 1],
        )


def exercise_name_selection(available_exercises: list) -> str:
    for index, exercise in enumerate(available_exercises):
        print(f"{index}: {exercise}")
    chosen_exercise = None
    while chosen_exercise is None:
        selection = input("Choose an exercise.")
        try:
            selection = int(selection)
            isInt = True
        except ValueError:
            selection = selection.upper()
            isInt = False

        if isInt and selection >= 0:
            try:
                chosen_exercise = available_exercises[selection]
            except IndexError:
                pass
        elif not isInt:
            chosen_exercise = selection if selection in available_exercises else None
        if chosen_exercise is None:
            print(f"Error: Invalid exercise: {selection}")

    return chosen_exercise


def target_reps_selection(available_target_reps: list) -> None | int:
    target_reps = None
    if len(available_target_reps) == 1:
        return None

    while target_reps is None:
        for rep_range in available_target_reps:
            print(f"{rep_range:.0f}, ", end="")
        print("or ENTER for no filter.")
        selection = input("Filter by target reps.")
        if selection == "":
            return None

        try:
            selection = int(selection)
        except ValueError:
            print(f"Invalid selection: {selection}")
            continue
        if selection in available_target_reps:
            target_reps = selection
            break
    return target_reps


def get_rep_ranges(df: pd.DataFrame, chosen_exercise: str) -> list[int]:
    target_reps = df.loc[
        (df["exerciseName"] == chosen_exercise, "targetReps")
    ].to_numpy(na_value=-1)
    target_reps = [int(item) for item in target_reps]
    target_reps = set(target_reps)

    if -1 in target_reps:
        target_reps.remove(-1)
    return sorted(target_reps)


def show_graph(sorted_workouts: list[Workout]):
    df = load_dataframe(sorted_workouts)
    available_exercises = list_available_exercises(df)
    exercise_to_plot = exercise_name_selection(available_exercises)
    rep_ranges = get_rep_ranges(df, exercise_to_plot)
    rep_range_selected = target_reps_selection(rep_ranges)
    plot_dataframe(df, exercise_to_plot, rep_range_selected)
