# pylint: disable=wrong-import-position,wrong-import-order,ungrouped-imports
"""
All-transitions performance test for SnackAttackTrack.

Walks through every meaningful screen transition, records frame times
for each, and outputs a structured JSON report.

Usage:
    python scripts/perf_test_all_transitions.py [--runs N] [--output PATH]
"""

import argparse
import asyncio
import json
import os
import shutil
import sys
import tempfile
import time

os.environ["MOCK_RFID_READER"] = "1"
os.environ["KIVY_NO_ARGS"] = "1"

from kivy.config import Config

Config.set("kivy", "pause_on_minimize", "0")
Config.set("kivy", "log_level", "error")

sys.path.insert(
    0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "GuiApp")
)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kivy.core.window import Window

Window.size = (800, 600)

from frame_profiler import FrameRecorder

import logger as app_logger
import logging as std_logging

app_logger.setup_logging(log_level=std_logging.WARNING)
logger = app_logger.get_logger(__name__)

SETTLE_SECONDS = 0.5
POST_SETTLE_SECONDS = 0.3
SCREEN_CHANGE_TIMEOUT = 5.0


async def wait_for_screen(app, screen_name, timeout=SCREEN_CHANGE_TIMEOUT):
    deadline = time.perf_counter() + timeout
    while time.perf_counter() < deadline:
        if app.screenManager.current == screen_name:
            return True
        await asyncio.sleep(0.02)
    return False


def click_first_user_widget(app):
    grid = app.screenManager.current_screen.ids.get("LoginScreenUserGridLayout")
    if not grid:
        return False
    for child in reversed(grid.children):
        if hasattr(child, "Clicked"):
            child.Clicked()
            return True
    return False


def build_transitions(app):  # pylint: disable=too-many-locals,too-many-statements
    T = []

    def splash_to_login(a):
        a.screenManager.current_screen.onPressed()

    T.append(("splashScreen→loginScreen", splash_to_login, "loginScreen"))

    def login_to_main(a):
        click_first_user_widget(a)

    T.append(("loginScreen→mainUserPage", login_to_main, "mainUserPage"))

    def main_to_buy(a):
        a.screenManager.current_screen.ids.buyOption.dispatch("on_release")

    T.append(("mainUserPage→buyScreen", main_to_buy, "buyScreen"))

    def buy_to_main(a):
        a.screenManager.current_screen.ids.cancelButton.dispatch("on_release")

    T.append(("buyScreen→mainUserPage", buy_to_main, "mainUserPage"))

    def main_to_wheel(a):
        a.screenManager.current_screen.ids.gambleOption.dispatch("on_release")

    T.append(("mainUserPage→wheelOfSnacksScreen", main_to_wheel, "wheelOfSnacksScreen"))

    def wheel_to_main(a):
        a.screenManager.current_screen.ids.header.dispatch("on_back_button_pressed")

    T.append(("wheelOfSnacksScreen→mainUserPage", wheel_to_main, "mainUserPage"))

    def main_to_profile(a):
        a.screenManager.current_screen.ids.profileOption.dispatch("on_release")

    T.append(("mainUserPage→profileScreen", main_to_profile, "profileScreen"))

    def profile_to_history(a):
        a.screenManager.current_screen.ids.historyOption.dispatch("on_release")

    T.append(("profileScreen→historyScreen", profile_to_history, "historyScreen"))

    def history_to_profile(a):
        a.screenManager.current_screen.ids.header.dispatch("on_back_button_pressed")

    T.append(("historyScreen→profileScreen", history_to_profile, "profileScreen"))

    def profile_to_stats(a):
        a.screenManager.current_screen.ids.statisticsOption.dispatch("on_release")

    T.append(
        ("profileScreen→userStatisticsScreen", profile_to_stats, "userStatisticsScreen")
    )

    def stats_to_profile(a):
        a.screenManager.current_screen.ids.header.dispatch("on_back_button_pressed")

    T.append(("userStatisticsScreen→profileScreen", stats_to_profile, "profileScreen"))

    def profile_to_main(a):
        a.screenManager.current_screen.ids.header.dispatch("on_back_button_pressed")

    T.append(("profileScreen→mainUserPage", profile_to_main, "mainUserPage"))

    def main_to_admin(a):
        header = a.screenManager.current_screen.ids.header
        if header.settings_button:
            header.settings_button.dispatch("on_release")
        else:
            a.screenManager.transitionToScreen("adminScreen")

    T.append(("mainUserPage→adminScreen", main_to_admin, "adminScreen"))

    def admin_to_snacks(a):
        a.screenManager.current_screen.ids.editSnacksOption.dispatch("on_release")

    T.append(("adminScreen→editSnacksScreen", admin_to_snacks, "editSnacksScreen"))

    def snacks_to_admin(a):
        a.screenManager.current_screen.ids.header.dispatch("on_back_button_pressed")

    T.append(("editSnacksScreen→adminScreen", snacks_to_admin, "adminScreen"))

    def admin_to_users(a):
        a.screenManager.current_screen.ids.editUsersOption.dispatch("on_release")

    T.append(("adminScreen→editUsersScreen", admin_to_users, "editUsersScreen"))

    def users_to_admin(a):
        a.screenManager.current_screen.ids.header.dispatch("on_back_button_pressed")

    T.append(("editUsersScreen→adminScreen", users_to_admin, "adminScreen"))

    def admin_to_store_stats(a):
        a.screenManager.current_screen.ids.storeStatsOption.dispatch("on_release")

    T.append(("adminScreen→storeStatsScreen", admin_to_store_stats, "storeStatsScreen"))

    def store_stats_to_admin(a):
        a.screenManager.current_screen.ids.header.dispatch("on_back_button_pressed")

    T.append(("storeStatsScreen→adminScreen", store_stats_to_admin, "adminScreen"))

    def admin_to_log(a):
        a.screenManager.current_screen.ids.logOption.dispatch("on_release")

    T.append(("adminScreen→logScreen", admin_to_log, "logScreen"))

    def log_to_admin(a):
        a.screenManager.current_screen.ids.header.dispatch("on_back_button_pressed")

    T.append(("logScreen→adminScreen", log_to_admin, "adminScreen"))

    def admin_to_settings(a):
        a.screenManager.current_screen.ids.systemSettingsOption.dispatch("on_release")

    T.append(
        (
            "adminScreen→editSystemSettingsScreen",
            admin_to_settings,
            "editSystemSettingsScreen",
        )
    )

    def settings_to_admin(a):
        a.screenManager.current_screen.ids.header.dispatch("on_back_button_pressed")

    T.append(("editSystemSettingsScreen→adminScreen", settings_to_admin, "adminScreen"))

    def admin_to_main(a):
        a.screenManager.current_screen.ids.header.dispatch("on_back_button_pressed")

    T.append(("adminScreen→mainUserPage", admin_to_main, "mainUserPage"))

    def main_to_login(a):
        a.screenManager.current_screen.ids.header.dispatch("on_back_button_pressed")

    T.append(("mainUserPage→loginScreen", main_to_login, "loginScreen"))

    return T


async def run_all_transitions(  # pylint: disable=too-many-locals,too-many-statements
    db_source_path: str, num_runs: int = 1
) -> list:
    from main import snackAttackTrackApp  # pylint: disable=import-outside-toplevel

    all_run_results = []

    for run_idx in range(num_runs):
        print(f"\n{'='*70}")
        print(f"  RUN {run_idx + 1}/{num_runs}")
        print(f"{'='*70}")

        db_path = os.path.join(tempfile.gettempdir(), f"perf_test_run_{run_idx}.db")
        shutil.copy2(db_source_path, db_path)
        settings_path = os.path.join(
            tempfile.gettempdir(), f"perf_test_settings_{run_idx}.json"
        )

        app = snackAttackTrackApp(
            use_inspector=False,
            settings_path=settings_path,
            database_path=db_path,
        )

        recorder = FrameRecorder()
        recorder.install()

        loop = asyncio.get_event_loop()
        loop.create_task(app.async_run(), name="kivy_event_loop")
        await asyncio.sleep(1.5)

        transitions = build_transitions(app)
        run_results = []

        for idx, (name, trigger, expected) in enumerate(transitions):
            print(f"  [{idx + 1}/{len(transitions)}] {name} ... ", end="", flush=True)
            recorder.start_transition(name)
            recorder.mark("pre_baseline")
            await asyncio.sleep(0.1)
            recorder.mark("trigger")
            try:
                trigger(app)
            except Exception as e:  # pylint: disable=broad-exception-caught
                recorder.mark(f"trigger_error: {e}")
                recorder.stop_transition()
                print(f"ERROR: {e}")
                continue

            recorder.mark("waiting_for_screen_change")
            changed = await wait_for_screen(app, expected)
            if changed:
                recorder.mark("screen_changed")
            else:
                recorder.mark(f"timeout: still_on_{app.screenManager.current}")

            await asyncio.sleep(SETTLE_SECONDS)
            recorder.mark("settled")
            await asyncio.sleep(POST_SETTLE_SECONDS)

            stats = recorder.stop_transition()
            run_results.append(stats)

            max_ms = stats.get("max_frame_ms", 0)
            avg_ms = stats.get("avg_frame_ms", 0)
            long_n = stats.get("frames_over_33ms", 0)
            status = "TIMEOUT" if not changed else "OK"
            print(f"{status}  max={max_ms:.1f}ms  avg={avg_ms:.1f}ms  >33ms={long_n}")

        app.screenManager.database.close()
        app.stop()
        await asyncio.sleep(0.5)
        for p in (db_path, settings_path):
            if os.path.exists(p):
                os.remove(p)

        all_avgs = [
            s.get("avg_frame_ms", 0) for s in run_results if s.get("avg_frame_ms")
        ]
        all_max = [
            s.get("max_frame_ms", 0) for s in run_results if s.get("max_frame_ms")
        ]
        long_total = sum(s.get("frames_over_33ms", 0) for s in run_results)
        worst = (
            max(run_results, key=lambda s: s.get("max_frame_ms", 0))
            if run_results
            else {}
        )
        run_output = {
            "run_number": run_idx + 1,
            "transitions": run_results,
            "aggregate": {
                "total": len(run_results),
                "passed": sum(1 for s in run_results if s.get("max_frame_ms", 0) > 0),
                "overall_avg_frame_ms": (
                    round(sum(all_avgs) / len(all_avgs), 2) if all_avgs else 0
                ),
                "overall_max_frame_ms": round(max(all_max), 2) if all_max else 0,
                "worst_transition": worst.get("name", ""),
                "worst_max_frame_ms": worst.get("max_frame_ms", 0),
                "total_long_frames": long_total,
            },
        }
        all_run_results.append(run_output)

    return all_run_results


def print_report(run_results):
    if not run_results:
        print("No results.")
        return

    first = run_results[0]
    transitions = first.get("transitions", [])
    agg = first.get("aggregate", {})

    print(f"\n{'='*80}")
    print(
        f"  ── REPORT ({len(run_results)} run{'s' if len(run_results) > 1 else ''}) ──"
    )
    print(f"{'='*80}")
    print(f"  {'Transition':<40} {'Max(ms)':>8} {'Avg(ms)':>8} {'>33ms':>6}")
    print(f"  {'-'*40} {'-'*8} {'-'*8} {'-'*6}")

    for t in transitions:
        name = t.get("name", "?")
        max_ms = t.get("max_frame_ms", 0)
        avg_ms = t.get("avg_frame_ms", 0)
        long_n = t.get("frames_over_33ms", 0)
        print(f"  {name:<40} {max_ms:>8.1f} {avg_ms:>8.1f} {long_n:>6}")

    a = agg
    print(f"\n  Aggregate: {a.get('passed', 0)}/{a.get('total', 0)} passed")
    print(f"  Overall avg frame: {a.get('overall_avg_frame_ms', 0):.1f} ms")
    print(f"  Overall max frame: {a.get('overall_max_frame_ms', 0):.1f} ms")
    print(
        f"  Worst transition:  {a.get('worst_transition', '')} ({a.get('worst_max_frame_ms', 0):.1f}ms)"
    )
    print(f"  Total long frames: {a.get('total_long_frames', 0)}")


def main():
    parser = argparse.ArgumentParser(description="Full transition performance test")
    parser.add_argument(
        "--runs", type=int, default=1, help="Number of full walk repetitions"
    )
    parser.add_argument(
        "--output", type=str, default=None, help="Path to write JSON results"
    )
    args = parser.parse_args()

    from seed_perf_db import create_database  # pylint: disable=import-outside-toplevel

    db_source = os.path.join(tempfile.gettempdir(), "perf_test_seed_source.db")
    db = create_database(db_source)
    db.close()

    print(f"Running transition test ({args.runs} run(s))...")
    all_results = asyncio.run(run_all_transitions(db_source, args.runs))
    print_report(all_results)

    if args.output:
        output = {"runs": all_results}
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2)
        print(f"\nResults saved to {args.output}")

    if os.path.exists(db_source):
        os.remove(db_source)


if __name__ == "__main__":
    main()
