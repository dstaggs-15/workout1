# Private workout source

Make this repository **private before adding personal files here**. A sign-in page cannot hide a CSV committed to a public repository, and deleting it later does not remove git history.

Upload one or more app-export CSV files here, then run **Actions → Analyze workouts → Run workflow**. Overlapping exports are deduplicated by workout start, exercise, set index, set type and recorded metrics. These fields must identify unique sets. Prefer one complete export when possible.

Use the provided export columns: `title,start_time,end_time,description,exercise_title,superset_id,exercise_notes,set_index,set_type,weight_lbs,reps,distance_miles,duration_seconds,rpe`. Dates use `Sep 30, 2026, 8:06 PM`. Empty rows are skipped; invalid nonempty rows fail with a row number.

Optional `muscle_overrides.json` maps exact exercise names to Chest, Back, Shoulders, Biceps, Triceps, Forearms, Quads, Hamstrings, Glutes, Calves or Core. Example: `{"Hip Adduction (Machine)":"Quads"}`. Mapping is a simplified primary-muscle attribution, not anatomical measurement.
