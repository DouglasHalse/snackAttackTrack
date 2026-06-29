"""
Frame-time profiler for Kivy screen transitions.

Records frame times via Clock.schedule_interval and provides per-transition
statistics for performance regression testing.

Usage:
    from frame_profiler import FrameRecorder

    recorder = FrameRecorder()
    recorder.install()
    recorder.start_transition("splashScreen→loginScreen")
    recorder.mark("about_to_tap")
    # ... trigger transition ...
    recorder.mark("screen_changed")
    # ... wait for settle ...
    recorder.mark("settled")
    recorder.stop_transition()
    print(recorder.last_stats)
"""

import os
import statistics
import sys
import time

sys.path.insert(
    0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "GuiApp")
)

# pylint: disable=wrong-import-position,wrong-import-order
from kivy.clock import Clock  # noqa: E402


class FrameRecorder:  # pylint: disable=too-many-instance-attributes
    """Records per-transition frame time statistics from the Kivy clock.

    A single FrameRecorder can measure multiple transitions in sequence.
    Call start_transition()/stop_transition() for each one.
    """

    # pylint: disable=too-many-arguments

    def __init__(self):
        self.installed = False
        self._frames = []
        self._recording = False
        self._start_time = 0.0
        self._current_transition = None
        self._transition_start_idx = 0
        self.per_transition_stats = []
        self.last_stats = None

    def install(self):
        """Start listening to the Kivy clock (idempotent)."""
        if self.installed:
            return
        Clock.schedule_interval(self._on_frame, 0)
        self.installed = True

    def _on_frame(self, dt):
        if not self._recording:
            return
        elapsed = time.perf_counter() - self._start_time
        dt_ms = dt * 1000
        self._frames.append((elapsed, dt_ms, "_frame"))

    def start_transition(self, name: str):
        """Begin recording a new named transition."""
        if self._current_transition is not None:
            self.stop_transition()
        self._current_transition = name
        self._start_time = time.perf_counter()
        self._recording = True
        self._transition_start_idx = len(self._frames)
        self.mark("begin")

    def mark(self, description: str):
        """Record a named event at the current time within the active transition."""
        if not self._recording:
            return
        elapsed = time.perf_counter() - self._start_time
        self._frames.append((elapsed, 0, description))

    def stop_transition(self) -> dict:
        """Stop recording the current transition, compute stats, return them."""
        self._recording = False
        name = self._current_transition or "unnamed"

        t_frames = self._frames[self._transition_start_idx :]
        frame_dts = [dt for _, dt, label in t_frames if label == "_frame"]
        events = [(t, label) for t, dt, label in t_frames if label != "_frame"]

        tap_time = next(
            (t for t, l in events if "tap" in l.lower() or "trigger" in l.lower()), None
        )
        change_time = next((t for t, l in events if l == "screen_changed"), None)
        settle_time = next((t for t, l in events if l == "settled"), None)

        stats = self._compute_frame_stats(
            name, frame_dts, events, tap_time, change_time, settle_time
        )
        stats["status"] = "ok" if frame_dts else "error"

        self._transition_start_idx = len(self._frames)
        self._current_transition = None
        self.per_transition_stats.append(stats)
        self.last_stats = stats
        return stats

    def start_recording(self):
        """Start a free-form recording session (not tied to a transition)."""
        self._frames = []
        self._current_transition = None
        self._start_time = time.perf_counter()
        self._recording = True

    def stop_recording(self):
        """Stop free-form recording and return raw frames."""
        self._recording = False
        return self._frames

    def compute_stats(self, name="freeform"):
        """Compute stats from the raw frame buffer for free-form recording."""
        frame_dts = [dt for _, dt, label in self._frames if label == "_frame"]
        events = [(t, label) for t, dt, label in self._frames if label != "_frame"]
        self.last_stats = self._compute_frame_stats(
            name, frame_dts, events, None, None, None
        )
        self.last_stats["status"] = "ok" if frame_dts else "error"
        return self.last_stats

    @staticmethod
    def _compute_frame_stats(
        name, frame_dts, events, tap_time, change_time, settle_time
    ):
        if not frame_dts:
            return {"name": name, "status": "error"}

        sorted_dts = sorted(frame_dts)
        n = len(frame_dts)

        long_frame_details = []
        frames_over_33 = 0
        frames_over_50 = 0
        max_dt = 0.0
        for i, dt in enumerate(frame_dts):
            if dt > 33.33:
                frames_over_33 += 1
                long_frame_details.append(
                    {
                        "frame_index": i,
                        "elapsed_ms": (i / 60) * 1000 if n > 0 else 0,
                        "duration_ms": round(dt, 2),
                    }
                )
            if dt > 50:
                frames_over_50 += 1
            max_dt = max(max_dt, dt)

        return {
            "name": name,
            "frame_count": n,
            "avg_frame_ms": round(statistics.mean(frame_dts), 2),
            "median_frame_ms": (
                round(statistics.median(frame_dts), 2)
                if n > 1
                else round(frame_dts[0], 2)
            ),
            "max_frame_ms": round(max_dt, 2),
            "min_frame_ms": round(min(frame_dts), 2),
            "stdev_frame_ms": round(statistics.stdev(frame_dts), 2) if n > 1 else 0,
            "p95_frame_ms": (
                round(sorted_dts[int(n * 0.95)], 2) if n > 1 else round(frame_dts[0], 2)
            ),
            "p99_frame_ms": (
                round(sorted_dts[int(n * 0.99)], 2) if n > 1 else round(frame_dts[0], 2)
            ),
            "frames_over_33ms": frames_over_33,
            "frames_over_50ms": frames_over_50,
            "pct_over_33ms": round(frames_over_33 / n * 100, 2) if n > 0 else 0,
            "long_frames": long_frame_details,
            "events": [(round(t * 1000, 1), l) for t, l in events],
            "transition_duration_ms": (
                round((settle_time or change_time or 0) * 1000, 1)
                if (settle_time or change_time)
                else 0
            ),
        }


# Legacy singleton API for backward compatibility
_global_recorder = FrameRecorder()


def install_frame_profiler():
    _global_recorder.install()


def start_recording():
    _global_recorder.start_recording()


def stop_recording():
    return _global_recorder.stop_recording()


def record_event(description):
    _global_recorder.mark(description)


def start_transition(name):
    _global_recorder.start_transition(name)


def stop_transition():
    return _global_recorder.stop_transition()
