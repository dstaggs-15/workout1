# Workout sources

Upload app CSV exports here or replace `workouts.csv`. A commit on main automatically runs **Analyze workouts** and republishes Pages. To rebuild manually: **Actions → Analyze workouts → Run workflow**.

Edit `profile.txt` for weight and height. Each changed profile is archived in `history/profile_history.json` by the workflow and committed to main. Add new weigh-in lines to preserve a current timeline; past archived versions remain available.

CSV columns: `title,start_time,end_time,description,exercise_title,superset_id,exercise_notes,set_index,set_type,weight_lbs,reps,distance_miles,duration_seconds,rpe`. Dates use `Sep 30, 2026, 8:06 PM`. Empty rows are skipped; invalid nonempty rows fail with a row number. Matching set identifiers **and recorded metrics** are deduplicated.

Optional `muscle_overrides.json` maps exact exercise names to Chest, Back, Shoulders, Biceps, Triceps, Forearms, Quads, Hamstrings, Glutes, Calves or Core.

These files and the dashboard are currently public.
