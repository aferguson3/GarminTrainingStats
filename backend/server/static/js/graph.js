exercise_info = function () {
  return JSON.parse(document.getElementById("exercise_info").value);
};

function clearSelects() {
  if (document.getElementById("categories").value !== "") {
    document.getElementById("categories").value = "";
  }
  document.getElementById("exercises").replaceChildren();
  document.getElementById("rep_ranges").replaceChildren();
}

function changeSelects() {
  document.addEventListener("DOMContentLoaded", clearSelects);
  document
    .getElementById("categories")
    .addEventListener("change", onCategoryChange);
  document
    .getElementById("exercises")
    .addEventListener("change", onExercisesChange);
}

function createOption(select_element, text, value) {
  let new_option = document.createElement("option");
  new_option.text = text;
  new_option.value = value;
  select_element.add(new_option);
}

function onCategoryChange() {
  let categories_select = document.getElementById("categories");
  let reps_ranges_select = document.getElementById("rep_ranges");
  changeExerciseOptions(categories_select.selectedOptions[0].label);
  reps_ranges_select.replaceChildren();
}

function onExercisesChange() {
  let exercise_name_select = document.getElementById("exercises");
  changeRepsOptions(exercise_name_select.selectedOptions[0].label);
}

function changeExerciseOptions(category) {
  let exercise_name_select = document.getElementById("exercises");
  let exercise_info_dict = exercise_info();
  exercise_name_select.replaceChildren();
  exercise_name_select.setAttribute("style", "visibility: visible;");
  createOption(exercise_name_select, "", "");

  for (let exercise_name in exercise_info_dict) {
    let display_name = exercise_name.replaceAll("_", " ");
    if (exercise_info_dict[exercise_name]["category"] === category) {
      createOption(
        exercise_name_select,
        toTitleCase(display_name),
        exercise_name,
      );
    }
  }
}

function changeRepsOptions(exercise_name) {
  let selected = exercise_name.toUpperCase().replaceAll(" ", "_");
  let reps_ranges_select = document.getElementById("rep_ranges");
  let exercise_info_dict = exercise_info();

  reps_ranges_select.replaceChildren();
  reps_ranges_select.setAttribute("style", "visibility: visible;");
  let new_rep_ranges = exercise_info_dict[selected]["rep_ranges"];
  createOption(reps_ranges_select, "", "");
  createOption(reps_ranges_select, "No Filter", "None");

  for (let i = 0; i < new_rep_ranges.length; i++) {
    createOption(reps_ranges_select, new_rep_ranges[i], new_rep_ranges[i]);
  }
}

function toTitleCase(str) {
  return str.replace(/\w\S*/g, function (txt) {
    return txt.charAt(0).toUpperCase() + txt.substring(1).toLowerCase();
  });
}

/* Main */
changeSelects();
