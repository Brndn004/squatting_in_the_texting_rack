const ROUTINES = {
  "beginner": {
    "name": "Beginner",
    "date_created": "2026-01-11-1768172397",
    "sessions": [
      "squat_horizontal_pushpull",
      "hinge_vertical_pushpull",
      "squat_upper_hypertrophy"
    ]
  }
};

const SESSIONS = {
  "hinge_vertical_pushpull": {
    "name": "Hinge + Vertical Push/Pull",
    "session_name": "hinge_vertical_pushpull",
    "exercises": [
      {
        "exercise_name": "barbell_deadlift",
        "sets": 2,
        "reps": 6,
        "percent_1rm": 0.8
      },
      {
        "exercise_name": "barbell_overhead_press",
        "sets": 3,
        "reps": 8,
        "percent_1rm": 0.8
      },
      {
        "exercise_name": "assisted_pull_up",
        "sets": 3,
        "reps": 10,
        "percent_1rm": 0.7
      },
      {
        "exercise_name": "dumbell_triceps_extension",
        "sets": 2,
        "reps": 15,
        "percent_1rm": 0.7
      },
      {
        "exercise_name": "dumbell_lateral_raise",
        "sets": 2,
        "reps": 15,
        "percent_1rm": 0.7
      }
    ],
    "date_created": "2026-01-11-1768172033"
  },
  "squat_horizontal_pushpull": {
    "name": "Squat + Horizontal Push/Pull",
    "session_name": "squat_horizontal_pushpull",
    "exercises": [
      {
        "exercise_name": "barbell_squat",
        "sets": 3,
        "reps": 8,
        "percent_1rm": 0.8
      },
      {
        "exercise_name": "barbell_bench_press",
        "sets": 3,
        "reps": 8,
        "percent_1rm": 0.8
      },
      {
        "exercise_name": "barbell_bent_over_row",
        "sets": 3,
        "reps": 10,
        "percent_1rm": 0.8
      },
      {
        "exercise_name": "dumbell_lateral_raise",
        "sets": 2,
        "reps": 15,
        "percent_1rm": 0.7
      },
      {
        "exercise_name": "dumbell_biceps_curl",
        "sets": 2,
        "reps": 15,
        "percent_1rm": 0.7
      }
    ],
    "date_created": "2026-01-11-1768171764"
  },
  "squat_upper_hypertrophy": {
    "name": "Squat + Upper Hypertrophy",
    "session_name": "squat_upper_hypertrophy",
    "exercises": [
      {
        "exercise_name": "barbell_squat",
        "sets": 3,
        "reps": 8,
        "percent_1rm": 0.8
      },
      {
        "exercise_name": "barbell_bent_over_row",
        "sets": 3,
        "reps": 10,
        "percent_1rm": 0.7
      },
      {
        "exercise_name": "dumbell_incline_bench_press",
        "sets": 3,
        "reps": 8,
        "percent_1rm": 0.7
      },
      {
        "exercise_name": "dumbell_biceps_curl",
        "sets": 2,
        "reps": 15,
        "percent_1rm": 0.7
      },
      {
        "exercise_name": "dumbell_triceps_extension",
        "sets": 2,
        "reps": 15,
        "percent_1rm": 0.7
      }
    ],
    "date_created": "2026-01-11-1768172147"
  }
};

const EXERCISES = {
  "assisted_pull_up": {
    "name": "Assisted Pull Up",
    "exercise_name": "assisted_pull_up",
    "1rm": {
      "lb": 0.0
    },
    "date_created": "2026-01-11-1768170939"
  },
  "barbell_bench_press": {
    "name": "Barbell Bench Press",
    "exercise_name": "barbell_bench_press",
    "1rm": {
      "lb": 135.0
    },
    "date_created": "2026-01-11-1768170558"
  },
  "barbell_bent_over_row": {
    "name": "Barbell Bent Over Row",
    "exercise_name": "barbell_bent_over_row",
    "1rm": {
      "lb": 0.0
    },
    "date_created": "2026-01-11-1768170776"
  },
  "barbell_deadlift": {
    "name": "Barbell Deadlift",
    "exercise_name": "barbell_deadlift",
    "1rm": {
      "lb": 175.0
    },
    "date_created": "2026-01-11-1768170918"
  },
  "barbell_overhead_press": {
    "name": "Barbell Overhead Press",
    "exercise_name": "barbell_overhead_press",
    "1rm": {
      "lb": 0.0
    },
    "date_created": "2026-01-11-1768170929"
  },
  "barbell_squat": {
    "name": "Barbell Squat",
    "exercise_name": "barbell_squat",
    "1rm": {
      "lb": 160.0
    },
    "date_created": "2026-01-11-1768170546"
  },
  "dumbell_biceps_curl": {
    "name": "Dumbell Biceps Curl",
    "exercise_name": "dumbell_biceps_curl",
    "1rm": {
      "lb": 0.0
    },
    "date_created": "2026-01-11-1768170796"
  },
  "dumbell_incline_bench_press": {
    "name": "Dumbell Incline Bench Press",
    "exercise_name": "dumbell_incline_bench_press",
    "1rm": {
      "lb": 0.0
    },
    "date_created": "2026-01-11-1768171085"
  },
  "dumbell_lateral_raise": {
    "name": "Dumbell Lateral Raise",
    "exercise_name": "dumbell_lateral_raise",
    "1rm": {
      "lb": 0.0
    },
    "date_created": "2026-01-11-1768170781"
  },
  "dumbell_triceps_extension": {
    "name": "Dumbell Triceps Extension",
    "exercise_name": "dumbell_triceps_extension",
    "1rm": {
      "lb": 0.0
    },
    "date_created": "2026-01-11-1768170967"
  }
};
