"""
1. Set up a Strava App.
2. In the playground, run a query for club activities.
3. Save that output in a file as `query_yyyy_mm_dd_hh-mm-ss.json`.
4. Run another query at some future time.
5. Save it in the same format.
6. Run this script.
7. Brag to your friends.
8. Cry a little that the Strava API is so brutal to require this sucky script
   instead of just providing the date field for each club activity. :(
"""

import dataclasses
import datetime
import json
import os
import pprint

from typing import Any


@dataclasses.dataclass(frozen=True, eq=False)
class Activity():
    # Things I care about.
    sport_type: str
    distance_meters: int

    # Things I care about for pseudo-uniqueness only.
    elapsed_time_s: int
    moving_time_s: int

    def __eq__(self, other):
        return all((self.sport_type == other.sport_type,
            self.distance_meters == other.distance_meters,
            self.elapsed_time_s == other.elapsed_time_s,
            self.moving_time_s == other.moving_time_s))


def get_file_names() -> list[str]:
    """
    Returns:
        Any file that starts with `query_`, assuming that all files take the form
        `query_yyyy_mm_dd_hh-MM-ss.json` (year, month, day, hour, minute, second).
    """
    files = [ff for ff in os.listdir(".") if os.path.isfile(ff) and ff.startswith("query_")]
    return files


def parse_activities(query_file: str) -> dict[str, Activity]:
    """
    Returns:
        {<athlete name>: <list of activities>}
    """
    with open(query_file, "r") as ff:
        lines = ff.readlines()
    activities = json.loads("".join(lines))
    activities_by_athlete = {}
    for activity in activities:
        athlete = activity["athlete"]["firstname"] + " " + activity["athlete"]["lastname"]
        sport = activity["sport_type"]
        distance_meters = activity["distance"]
        elapsed_s = activity["elapsed_time"]
        moving_s = activity["moving_time"]
        if athlete not in activities_by_athlete:
            activities_by_athlete[athlete] = []
        activities_by_athlete[athlete].append(
            Activity(sport, distance_meters, elapsed_s, moving_s)
        )
    return activities_by_athlete


def get_diff(per_athlete_1: dict[str, list[Activity]], per_athlete_2: dict[str, list[Activity]]) -> dict[str, list[Activity]]:
    """
    Assumes:
        * If the contents of an Activity are different, then that is a unique activity.
        * Performance doesn't matter (list iteration comparison).

    Returns:
        Any content in per_athlete_2 that is not in per_athlete_1.
    """
    unique_activities = {}
    for athlete, maybe_new_activities in per_athlete_2.items():
        if athlete not in per_athlete_1.keys():
            unique_activities[athlete] = maybe_new_activities
            continue

        # This athlete is in the first dict.
        for maybe_new_activity in maybe_new_activities:
            # Lol performance wut?
            for old_activity in per_athlete_1[athlete]:
                if maybe_new_activity != old_activity:
                    if athlete not in unique_activities:
                        unique_activities[athlete] = []
                    unique_activities[athlete].append(maybe_new_activity)
                    break
    return unique_activities


def count_runs(activities_by_athlete: dict[str, list[Activity]], threshold_meters: int) -> dict[str, int]:
    """
    Returns:
        {"<runner name>": <runs over threshold>}
    """
    runs_over_threshold = {}
    for athlete, activities in activities_by_athlete.items():
        runs_over_threshold[athlete] = 0
        for activity in activities:
            if activity.sport_type == "Run" and activity.distance_meters > threshold_meters:
                runs_over_threshold[athlete] += 1
    return runs_over_threshold


def main():
    all_files = sorted(get_file_names())
    activities_older_query = parse_activities(all_files[-2])
    activities_newer_query = parse_activities(all_files[-1])
    new_activities_by_athlete = get_diff(activities_older_query, activities_newer_query)
    valid_runs_per_athlete = count_runs(new_activities_by_athlete, 400)  # 0.25 miles ~= 400 meters
    pprint.pprint(valid_runs_per_athlete)


if __name__ == "__main__":
    main()
