import dataclasses
import pathlib
from typing import Any

from rau.tools.torch.saver import read_logs
from rau.tools.logging import LogParseError, LogEvent

@dataclasses.dataclass
class Trial:
    info: dict[str, dict[str, Any]]
    events: list[LogEvent] | None
    path: pathlib.Path

def read_data_for_trial(dirname, capture_all_events):
    required_event_types = { 'model_info', 'train' }
    info = {}
    if capture_all_events:
        all_events = []
    else:
        all_events = None
    try:
        with read_logs(dirname) as events:
            for event in events:
                if event.type in required_event_types:
                    info[event.type] = event.data
                if capture_all_events:
                    all_events.append(event)
    except (FileNotFoundError, LogParseError):
        pass
    if len(info) != len(required_event_types):
        return None
    return Trial(info, all_events, dirname)

def read_data_for_multiple_trials(trial_dirs, capture_all_events):
    trials = []
    missing_dirs = []
    for trial_dir in trial_dirs:
        trial = read_data_for_trial(trial_dir, capture_all_events)
        if trial is not None:
            trials.append(trial)
        else:
            missing_dirs.append(trial_dir)
    return trials, missing_dirs
