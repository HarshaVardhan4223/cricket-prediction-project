"""Augment player JSON with physiology fields.

Usage:
  - By default this script creates a backup of the input JSON and writes an augmented file.
  - You can optionally provide a CSV with sensor data to merge by `player_id`.

Example:
  python augment_players_with_physiology.py \
    --input data/global_cricket_players_fixed.json \
    --output data/global_cricket_players_fixed_augmented.json \
    --merge-csv data/physio_updates.csv

The script adds these fields for every player if missing:
  resting_hr, avg_hr, hrv_rmssd, stress_score, systolic_bp, diastolic_bp,
  sleep_hours, sleep_score, hydration_level, readiness_score, last_update_source

Fields are initialized to null (None) so you can merge real sensor/API data later.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
from typing import Dict, Any, List


DEFAULT_FIELDS = {
    "resting_hr": None,
    "avg_hr": None,
    "hrv_rmssd": None,
    "stress_score": None,
    "systolic_bp": None,
    "diastolic_bp": None,
    "sleep_hours": None,
    "sleep_score": None,
    "hydration_level": None,
    "readiness_score": None,
    "last_update_source": None,
}


DEFAULT_INSIGHTS = {
    "player_insights": {
        "physiological_profile": {
            "resting_heart_rate_bpm": None,
            "optimal_in_game_hr_bpm": None,
            "hrv_readiness_level": None,
            "hrv_score_range": None,
            "recovery_speed": None,
            "pressure_zone_performance": None,
            "stress_management_technique": None,
        },
        "mental_toughness": {
            "clutch_performance_rating": None,
            "known_for": None,
            "chase_master": None,
            "death_over_specialist": None,
            "routine_strength": None,
        },
        "wearable_tech_usage": {
            "device": None,
            "daily_monitoring": None,
            "readiness_prediction": None,
        },
        "performance_prediction": {
            "big_game_probability": None,
            "fatigue_risk": None,
            "injury_risk": None,
        },
        "coach_note": None,
    }
}


DEFAULT_INSIGHTS_VALUES = {
    "physiological_profile": {
        "resting_heart_rate_bpm": "45-55",
        "optimal_in_game_hr_bpm": "140-165",
        "hrv_readiness_level": "High",
        "hrv_score_range": "75-90",
        "recovery_speed": "Excellent (HR drops 40+ BPM in 1 min after sprint)",
        "pressure_zone_performance": "Thrives in high arousal (Inverted U peak)",
        "stress_management_technique": "Box breathing + visualization",
    },
    "mental_toughness": {
        "clutch_performance_rating": "9.5/10",
        "known_for": "Ice-cool under pressure, big-match player",
        "chase_master": "Yes",
        "death_over_specialist": "Yes (batting/bowling)",
        "routine_strength": "Strong pre-shot/delivery routine reduces anxiety",
    },
    "wearable_tech_usage": {
        "device": "Fittr Hart Ring / WHOOP Strap",
        "daily_monitoring": "HRV, Sleep Score, Strain",
        "readiness_prediction": "85% chance of peak performance if morning HRV >75",
    },
    "performance_prediction": {
        "big_game_probability": "High (80%+ chance of impactful innings in knockouts)",
        "fatigue_risk": "Low (excellent recovery metrics)",
        "injury_risk": "Low (rapid HR recovery post-intensity)",
    },
    "coach_note": "Elite mental composure. Use in high-pressure situations. Monitor HRV before finals.",
}


def load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(obj: Any, path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)


def backup_file(src: str) -> str:
    base = os.path.splitext(src)[0]
    backup = f"{base}.backup.json"
    shutil.copy2(src, backup)
    return backup


def ensure_fields(player: Dict[str, Any], fields: Dict[str, Any]) -> None:
    for k, v in fields.items():
        if k not in player:
            player[k] = v


def ensure_insights(player: Dict[str, Any], insights_template: Dict[str, Any]) -> None:
    # Add the full insights structure if missing, but don't overwrite existing insights
    if "player_insights" not in player:
        player["player_insights"] = json.loads(json.dumps(insights_template["player_insights"]))


def merge_csv_updates(players: List[Dict[str, Any]], csv_path: str, id_key: str = "player_id") -> int:
    # Expect CSV with header matching field names and a column for id_key
    updated = 0
    with open(csv_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)

    # Create index by id_key for quick lookup
    index = {}
    for p in players:
        pid = p.get(id_key) or p.get("id") or p.get("player_id")
        if pid is not None:
            index[str(pid)] = p

    def set_nested(target: Dict[str, Any], dotted_key: str, value: Any) -> None:
        """Set a nested value on a dict given a dotted path, creating dicts as needed."""
        parts = dotted_key.split(".")
        cur = target
        for part in parts[:-1]:
            if part not in cur or not isinstance(cur[part], dict):
                cur[part] = {}
            cur = cur[part]
        cur[parts[-1]] = value

    for row in rows:
        pid = row.get(id_key) or row.get("id") or row.get("player_id")
        if pid is None:
            continue
        p = index.get(str(pid))
        if not p:
            continue
        for col, val in row.items():
            if col == id_key:
                continue
            if val == "" or val is None:
                continue
            # Try to convert numeric fields
            out_val: Any = val
            try:
                num = float(val)
                if num.is_integer():
                    num = int(num)
                out_val = num
            except Exception:
                out_val = val

            # Support dot-separated column names to merge into nested structures
            if "." in col:
                set_nested(p, col, out_val)
            else:
                p[col] = out_val

        # record update source in both top-level and inside player_insights for traceability
        p["last_update_source"] = os.path.basename(csv_path)
        if not isinstance(p.get("player_insights"), dict):
            p.setdefault("player_insights", {})
        p["player_insights"]["last_update_source"] = os.path.basename(csv_path)
        updated += 1

    return updated


def main() -> None:
    parser = argparse.ArgumentParser(description="Augment players JSON with physiology fields")
    parser.add_argument("--input", default="data/global_cricket_players_fixed.json")
    parser.add_argument("--output", default="data/global_cricket_players_fixed_augmented.json")
    parser.add_argument("--merge-csv", default=None, help="Optional CSV to merge updates from")
    parser.add_argument("--populate-defaults", action="store_true", help="Populate player_insights with realistic default values")
    parser.add_argument("--derive-insights", action="store_true", help="Derive per-player insights heuristically from available stats")
    parser.add_argument("--derive-insights-rich", action="store_true", help="Derive rich narrative per-player insights (detailed, human-readable)")
    parser.add_argument("--id-key", default="player_id", help="CSV and JSON id key to match players (default: player_id)")
    args = parser.parse_args()

    if not os.path.isfile(args.input):
        print(f"Input file not found: {args.input}")
        return

    print(f"Loading: {args.input}")
    data = load_json(args.input)

    # JSON can be a list of players or an object with a list inside
    if isinstance(data, dict):
        # Try common keys that may contain players list
        if "players" in data and isinstance(data["players"], list):
            players = data["players"]
            container = data
            container_is_dict_with_players = True
        else:
            # Assume top-level dict where each key is player id -> data
            players = []
            for k, v in data.items():
                if isinstance(v, dict):
                    v.setdefault("player_id", k)
                    players.append(v)
            container = data
            container_is_dict_with_players = False
    elif isinstance(data, list):
        players = data
        container = data
        container_is_dict_with_players = False
    else:
        print("Unrecognized JSON structure. Expecting list or dict of players.")
        return

    # Ensure fields
    for p in players:
        ensure_fields(p, DEFAULT_FIELDS)
        ensure_insights(p, DEFAULT_INSIGHTS)

    # Optionally populate realistic defaults into player_insights where missing
    def populate_defaults(players_list: List[Dict[str, Any]]) -> int:
        filled = 0
        for pl in players_list:
            ins = pl.setdefault("player_insights", {})
            # physiological_profile
            phys = ins.setdefault("physiological_profile", {})
            for k, v in DEFAULT_INSIGHTS_VALUES["physiological_profile"].items():
                if not phys.get(k):
                    phys[k] = v
            # mental_toughness
            ment = ins.setdefault("mental_toughness", {})
            for k, v in DEFAULT_INSIGHTS_VALUES["mental_toughness"].items():
                if not ment.get(k):
                    ment[k] = v
            # wearable_tech_usage
            wear = ins.setdefault("wearable_tech_usage", {})
            for k, v in DEFAULT_INSIGHTS_VALUES["wearable_tech_usage"].items():
                if not wear.get(k):
                    wear[k] = v
            # performance_prediction
            perf = ins.setdefault("performance_prediction", {})
            for k, v in DEFAULT_INSIGHTS_VALUES["performance_prediction"].items():
                if not perf.get(k):
                    perf[k] = v
            # coach_note
            if not ins.get("coach_note"):
                ins["coach_note"] = DEFAULT_INSIGHTS_VALUES.get("coach_note")
            filled += 1
        return filled

    # Backup
    backup = backup_file(args.input)
    print(f"Backup created: {backup}")

    # Merge optional CSV updates
    if args.merge_csv:
        if os.path.isfile(args.merge_csv):
            updated_count = merge_csv_updates(players, args.merge_csv, id_key=args.id_key)
            print(f"Merged updates for {updated_count} players from {args.merge_csv}")
        else:
            print(f"CSV file not found: {args.merge_csv}")

    # Save out
    print(f"Saving augmented file to: {args.output}")
    if container_is_dict_with_players and isinstance(container, dict):
        container["players"] = players
        # populate defaults if requested
        if args.populate_defaults:
            count = populate_defaults(players)
            print(f"Populated player_insights defaults for {count} players")
        if args.derive_insights:
            derived = derive_insights(players)
            print(f"Derived insights for {derived} players using heuristics")
        if args.derive_insights_rich:
            derived = derive_insights_rich(players)
            print(f"Derived rich narrative insights for {derived} players")
        save_json(container, args.output)
    else:
        if args.populate_defaults:
            count = populate_defaults(players)
            print(f"Populated player_insights defaults for {count} players")
        if args.derive_insights:
            derived = derive_insights(players)
            print(f"Derived insights for {derived} players using heuristics")
        if args.derive_insights_rich:
            derived = derive_insights_rich(players)
            print(f"Derived rich narrative insights for {derived} players")
        save_json(players, args.output)


def derive_insights(players: List[Dict[str, Any]]) -> int:
    """Fill player_insights with per-player heuristic estimates based on stats."""
    count = 0
    for p in players:
        name = p.get("player_name") or p.get("name") or "Player"
        age = p.get("age") or 30
        role = (p.get("role") or "").lower()
        is_young = str(p.get("is_young_star") or "No").lower() in ("yes", "true", "y")

        ins = p.setdefault("player_insights", {})
        phys = ins.setdefault("physiological_profile", {})

        # resting HR heuristic
        matches_total = 0
        for key in ("odi_matches", "t20i_matches", "ipl_matches", "test_matches"):
            v = p.get(key)
            if isinstance(v, (int, float)):
                matches_total += int(v)

        if age <= 28 and matches_total > 80:
            phys["resting_heart_rate_bpm"] = "45-53"
        elif age <= 32:
            phys["resting_heart_rate_bpm"] = "50-58"
        else:
            phys["resting_heart_rate_bpm"] = "54-66"

        # optimal in-game HR based on role
        if "bowler" in role or "fast" in role:
            phys["optimal_in_game_hr_bpm"] = "150-170"
        else:
            phys["optimal_in_game_hr_bpm"] = "138-160"

        # HRV readiness (simple heuristic)
        if is_young and matches_total < 100:
            phys["hrv_readiness_level"] = "High"
            phys["hrv_score_range"] = "75-90"
        elif matches_total > 300 or age > 33:
            phys["hrv_readiness_level"] = "Medium"
            phys["hrv_score_range"] = "60-74"
        else:
            phys["hrv_readiness_level"] = "High"
            phys["hrv_score_range"] = "68-80"

        # recovery speed: fast for younger batsmen, slower for fast bowlers and older players
        if ("fast" in role and age > 30) or matches_total > 400:
            phys["recovery_speed"] = "Moderate (Longer HR recovery after intense spells)"
        elif age < 27:
            phys["recovery_speed"] = "Elite (35+ BPM drop in 60s)"
        else:
            phys["recovery_speed"] = "Good (25-35 BPM drop in 60s)"

        # pressure zone performance: infer from averages/strike rates
        try:
            odi_avg = float(p.get("odi_average") or 0)
            ipl_avg = float(p.get("ipl_average") or 0)
            t20i_sr = float(p.get("t20i_strike_rate") or 0)
        except Exception:
            odi_avg = 0
            ipl_avg = 0
            t20i_sr = 0

        if odi_avg >= 45 or ipl_avg >= 40 or t20i_sr >= 140:
            phys["pressure_zone_performance"] = "Thrives in high arousal (Inverted U peak)"
        else:
            phys["pressure_zone_performance"] = "Moderate - benefits from controlled arousal"

        phys.setdefault("stress_management_technique", "Box breathing + visualization")

        # pressure handling mechanics
        mech = ins.setdefault("pressure_handling_mechanics", {})
        # brief narrative using name and role
        mech["situation_response"] = f"{name} shows stable physiological response in high-leverage moments; HR fluctuations typically limited, maintaining motor control."
        if odi_avg >= 40 or ipl_avg >= 38:
            mech["clutch_play_style"] = "Calculative risk management under pressure (high match-impact)"
            mech["mental_toughness_rating"] = f"{round(min(10, 5 + (odi_avg or ipl_avg) / 10),1)}/10"
        else:
            mech["clutch_play_style"] = "Needs structured routines to excel under pressure"
            mech["mental_toughness_rating"] = f"{round(min(9, 4 + (odi_avg or ipl_avg) / 12),1)}/10"

        mech["leadership_under_fire"] = "Calm presence" if (p.get("teams") and "captain" in str(p.get("roles", "")).lower()) else "Supportive leader"
        mech["routine_strength"] = "Strong pre-action routines" if is_young or odi_avg >= 40 else "Moderate routines"

        # wearable tech usage defaults
        wear = ins.setdefault("wearable_tech_usage", {})
        wear.setdefault("device", "WHOOP / Oura / Ultrahuman")
        wear.setdefault("daily_monitoring", "HRV, Sleep, Strain")
        wear.setdefault("readiness_prediction", "Higher readiness when HRV >70 and sleep_score high")

        # performance prediction
        perf = ins.setdefault("performance_prediction", {})
        # big_game_probability based on clutch rating numeric
        try:
            numeric = float(mech["mental_toughness_rating"].split("/")[0])
        except Exception:
            numeric = 6.0
        if numeric >= 8.5:
            perf["big_game_probability"] = "High (80%+)"
        elif numeric >= 7.0:
            perf["big_game_probability"] = "Good (60-80%)"
        else:
            perf["big_game_probability"] = "Moderate (40-60%)"

        # fatigue and injury risk heuristic
        if "fast" in role and age > 30:
            perf["fatigue_risk"] = "Moderate-High"
            perf["injury_risk"] = "Moderate"
        else:
            perf["fatigue_risk"] = "Low"
            perf["injury_risk"] = "Low"

        # coach note
        ins.setdefault("coach_note", f"Monitor HRV before tours; tailor workload for {name}.")

        # trace
        ins.setdefault("last_update_source", "derived_heuristics")
        p.setdefault("last_update_source", "derived_heuristics")

        count += 1
    return count


def derive_insights_rich(players: List[Dict[str, Any]]) -> int:
    """Produce a rich narrative `player_insights` block for each player using available stats.

    This creates human-readable narratives similar to the sample provided by the user,
    inserting the player's name and tailoring a few numeric ranges from stats.
    """
    # Precompute population distributions for key metrics so we can assign percentiles
    def safe_float_local(d, k):
        try:
            return float(d.get(k) or 0)
        except Exception:
            return 0.0

    odi_avgs = [safe_float_local(pp, "odi_average") for pp in players]
    ipl_avgs = [safe_float_local(pp, "ipl_average") for pp in players]
    t20i_srs = [safe_float_local(pp, "t20i_strike_rate") for pp in players]
    matches_totals = [int((safe_float_local(pp, "odi_matches") + safe_float_local(pp, "t20i_matches") + safe_float_local(pp, "ipl_matches")) or 0) for pp in players]

    def percentile(arr: List[float], value: float) -> float:
        # return percentile 0-100 of value within arr
        if not arr:
            return 50.0
        s = sorted([x for x in arr if x is not None])
        if not s:
            return 50.0
        # handle extremes
        if value <= s[0]:
            return 0.0
        if value >= s[-1]:
            return 100.0
        # linear interpolate
        for i in range(1, len(s)):
            if value <= s[i]:
                lo = s[i-1]
                hi = s[i]
                pos = (value - lo) / (hi - lo) if hi != lo else 0.0
                return (i-1 + pos) / (len(s)-1) * 100.0
        return 100.0

    count = 0
    for p in players:
        name = p.get("player_name") or p.get("name") or "Player"
        age = p.get("age") or 30
        role = (p.get("role") or "").strip()
        is_young = str(p.get("is_young_star") or "No").lower() in ("yes", "true", "y")

        # compute some numeric heuristics
        def safe_float(k):
            try:
                return float(p.get(k) or 0)
            except Exception:
                return 0.0

        odi_avg = safe_float("odi_average")
        ipl_avg = safe_float("ipl_average")
        t20i_sr = safe_float("t20i_strike_rate")
        matches_total = int((safe_float("odi_matches") + safe_float("t20i_matches") + safe_float("ipl_matches")) or 0)

        ins = p.setdefault("player_insights", {})

        # physiological_profile
        phys = {
            "resting_heart_rate_bpm": None,
            "optimal_in_game_hr_bpm": None,
            "hrv_readiness_level": None,
            "hrv_score_range": None,
            "recovery_speed": None,
            "pressure_zone_performance": None,
            "stress_management_technique": None,
        }

        # compute percentiles for this player
        odi_pct = percentile(odi_avgs, odi_avg)
        ipl_pct = percentile(ipl_avgs, ipl_avg)
        t20i_pct = percentile(t20i_srs, t20i_sr)
        matches_pct = percentile(matches_totals, matches_total)

        # resting HR ranges derived from age and fitness/workload percentile
        if matches_pct >= 75 and age < 30:
            phys["resting_heart_rate_bpm"] = "44-50"
        elif matches_pct >= 50 and age <= 32:
            phys["resting_heart_rate_bpm"] = "46-54"
        elif age > 33 or matches_pct < 30:
            phys["resting_heart_rate_bpm"] = "52-62"
        else:
            phys["resting_heart_rate_bpm"] = "48-56"

        # optimal HR nuanced by role and percentile
        if "fast" in role.lower() or "bowler" in role.lower():
            if matches_pct >= 75:
                phys["optimal_in_game_hr_bpm"] = "150-175"
            else:
                phys["optimal_in_game_hr_bpm"] = "148-170"
        else:
            if ipl_pct >= 70 or t20i_pct >= 70:
                phys["optimal_in_game_hr_bpm"] = "140-165"
            else:
                phys["optimal_in_game_hr_bpm"] = "136-158"

        # HRV readiness and score range based on percentile
        avg_pct = (odi_pct + ipl_pct + t20i_pct) / 3.0
        if avg_pct >= 75:
            phys["hrv_readiness_level"] = "High (ANS Stability)"
            phys["hrv_score_range"] = "74-90"
        elif avg_pct >= 45:
            phys["hrv_readiness_level"] = "Moderate-High"
            phys["hrv_score_range"] = "66-76"
        else:
            phys["hrv_readiness_level"] = "Moderate"
            phys["hrv_score_range"] = "58-70"

        # recovery speed: faster for higher percentile players and younger age
        if avg_pct >= 75 and age < 30:
            phys["recovery_speed"] = "Elite (35+ BPM drop in 60s)"
        elif "fast" in role.lower() and age > 30:
            phys["recovery_speed"] = "Moderate (Longer HR recovery after intense spells)"
        elif avg_pct >= 50:
            phys["recovery_speed"] = "Good (28-35 BPM drop in 60s)"
        else:
            phys["recovery_speed"] = "Average (20-30 BPM drop in 60s)"

        # pressure zone performance: use percentile and key stats
        if avg_pct >= 75 or t20i_pct >= 80:
            phys["pressure_zone_performance"] = "Peak Inverted-U (Maintains cognitive clarity at high arousal)"
        elif avg_pct >= 50:
            phys["pressure_zone_performance"] = "Handles pressure well with structured routines"
        else:
            phys["pressure_zone_performance"] = "Benefits from anxiety-reduction routines and controlled arousal"

        phys["stress_management_technique"] = "Vagal Tone Activation (Rhythmic breathing) + Mindfulness"

        ins["physiological_profile"] = phys

        # pressure_handling_mechanics: craft a richer narrative using player name and stats
        mech = {}
        mech["situation_response"] = (
            f"{name} displays strong cognitive separation between match importance and execution. "
            "Physiological markers (HR & HRV) suggest maintained motor control in high-leverage moments, "
            "with limited spike magnitude compared to peers."
        )

        # clutch play style
        if (odi_avg and odi_avg >= 45) or (ipl_avg and ipl_avg >= 40) or (t20i_sr and t20i_sr >= 140):
            mech["clutch_play_style"] = (
                "Adapts from aggression to calculated risk in pressure chases; uses trigger movements and field structure to "
                "create scoring opportunities while minimizing late-game panic."
            )
            mech["mental_toughness_rating"] = f"{round(min(10, 5 + (odi_avg or ipl_avg)/10),1)}/10"
        else:
            mech["clutch_play_style"] = (
                "Relies on structured pre-action routines to maintain focus; may benefit from additional mental-skills training "
                "for highest-leverage scenarios."
            )
            mech["mental_toughness_rating"] = f"{round(min(9, 4 + (odi_avg or ipl_avg)/12),1)}/10"

        mech["leadership_under_fire"] = (
            "Low-Arousal Leadership (calm presence that stabilizes teammates)" if "captain" in (p.get("role", "").lower() + " " + str(p.get("teams", "")).lower()) else "Supportive leader"
        )
        mech["routine_strength"] = (
            "Ritualistic physical and visual checks (glove/sight-screen) acting as neurological reset triggers" if is_young or mech["mental_toughness_rating"].startswith("8") else "Consistent routines"
        )

        ins["pressure_handling_mechanics"] = mech

        # wearable_tech_usage
        wear = {
            "device": "WHOOP 4.0 / Ultrahuman Ring Air",
            "daily_monitoring": "Strain vs. Recovery (Focus on Travel Strain)",
            "readiness_prediction": "Peak performance when HRV >72 and Sleep Latency <15 mins."
        }
        ins["wearable_tech_usage"] = wear

        # performance_prediction
        perf = {}
        # big game probability narrative
        try:
            mt = float(mech["mental_toughness_rating"].split("/")[0])
        except Exception:
            mt = 6.5

        if mt >= 8.5:
            perf["big_game_probability"] = "Elite (80%+ chance of impactful performance in knockouts)"
        elif mt >= 7.0:
            perf["big_game_probability"] = "High (60-80%)"
        else:
            perf["big_game_probability"] = "Moderate (40-60%)"

        # fatigue & injury risk
        if "fast" in role.lower() and age > 30:
            perf["fatigue_risk"] = "Moderate-High (monitor workloads)"
            perf["injury_risk"] = "Moderate"
        else:
            perf["fatigue_risk"] = "Low"
            perf["injury_risk"] = "Low"

        ins["performance_prediction"] = perf

        # coach_note
        ins["coach_note"] = (
            f"{name} shows elite mental composure and a prolonged 'Quiet Eye' under pressure. "
            "Recommend monitoring HRV before long tours and tailoring workload during high-density schedules."
        )

        # trace
        ins.setdefault("last_update_source", "derived_rich_heuristics")
        p.setdefault("last_update_source", "derived_rich_heuristics")

        count += 1
    return count

    print("Done.")


if __name__ == "__main__":
    main()
