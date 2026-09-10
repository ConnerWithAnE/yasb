import os
import re
from enum import Enum
from pathlib import Path
from typing import Self

from pydantic import BaseModel
from PyQt6.QtCore import QObject, QUrl

AVAIL_RE = re.compile(r"availability:\s*([A-Za-z]+)", re.IGNORECASE)
UNREAD_RE = re.compile(r"unread notification count:\s*(\d+)", re.IGNORECASE)


class AvailabilityDot(Enum):
    standard = "\u25cf"  # 0x25CF
    dnd = "\u2296"  # 0x2296
    ring = "\u25cb"  # 0x25CB


class AvailabilityStatusText(Enum):
    Available = "Available"
    AvailableIdle = "Available Idle"
    Away = "Away"
    BeRightBack = "Be Right Back"
    Busy = "Busy"
    InAMeeting = "In A Meeting"
    InACall = "In A Call"
    Presenting = "Presenting"
    OnThePhone = "On The Phone"
    DoNotDisturb = "Do Not Disturb"
    Focusing = "Focusing"
    Offline = "Offline"

    @classmethod
    def to_status(cls, token: str) -> Self | None:
        return cls.__members__.get(token)  # the member, or None if unknown


class AvailabilityStatusClass(Enum):
    Available = "available"
    AvailableIdle = "available-idle"
    Away = "away"
    BeRightBack = "be-right-back"
    Busy = "busy"
    InAMeeting = "in-a-meeting"
    InACall = "in-a-call"
    Presenting = "presenting"
    OnThePhone = "on-the-phone"
    DoNotDisturb = "do-not-disturb"
    Focusing = "focusing"
    Offline = "offline"

    @classmethod
    def to_class(cls, token: str) -> Self | None:
        return cls.__members__.get(token)  # the member, or None if unknown


class AvailabilityStatus(BaseModel):
    status: AvailabilityStatusText
    status_class: AvailabilityStatusClass
    unread: int
    dot: AvailabilityDot


class MSTeamsStatusAPI(QObject):
    AvailabilityDot = AvailabilityDot

    _instance: MSTeamsStatusAPI | None = None

    @classmethod
    def get_instance(cls, parent: QObject, url: QUrl = None):
        if cls._instance is not None:
            return cls._instance
        cls._instance = MSTeamsStatusAPI(parent, url)
        return cls._instance

    def __init__(self, parent: QObject, url: QUrl = None):
        super().__init__(parent)

        self._teams_log_dir = MSTeamsStatusAPI._find_teams_log_dir()
        self._teams_log_file = MSTeamsStatusAPI._find_latest_teams_log(self._teams_log_dir)

        self._tail = 8000

    def get_status(self):
        if self._teams_log_dir is None:
            if self._teams_log_dir is None:
                self._teams_log_dir = MSTeamsStatusAPI._find_teams_log_dir()
            self._teams_log_file = MSTeamsStatusAPI._find_latest_teams_log(self._teams_log_dir)
        status, unread = self._find_status()
        status_member = AvailabilityStatusText.to_status(status)
        status_value = AvailabilityStatus(
            status=status_member,
            status_class=AvailabilityStatusClass.to_class(status),
            unread=unread,
            dot=self.dot_for(status_member),
        )

        return status_value

    @staticmethod
    def dot_for(status: AvailabilityStatusText | None) -> AvailabilityDot:
        if status in {AvailabilityStatusText.DoNotDisturb, AvailabilityStatusText.Focusing}:
            return AvailabilityDot.dnd
        if status is AvailabilityStatusText.Offline:
            return AvailabilityDot.ring
        return AvailabilityDot.standard

    def _find_status(self):
        avail_match = None
        notif_match = None
        lines = MSTeamsStatusAPI._tail_lines(self._teams_log_file, self._tail)

        for line in reversed(lines):
            if avail_match is None:
                avail_match = AVAIL_RE.search(line)
            if notif_match is None:
                notif_match = UNREAD_RE.search(line)
            if avail_match is not None and notif_match is not None:
                return (avail_match.group(1), int(notif_match.group(1)))
        return (avail_match.group(1) if avail_match else None, int(notif_match.group(1)) if notif_match else None)

    @classmethod
    def ms_teams_timer_start(cls):
        return

    @staticmethod
    def _find_teams_log_dir() -> Path | None:
        """Locate the new Teams Logs directory, or None if not found."""
        local = os.environ.get("LOCALAPPDATA")
        if not local:
            return None

        packages = Path(local) / "Packages"
        if not packages.is_dir():
            return None

        # Don't trust the exact family name — match any MSTeams_* package.
        for pkg in packages.glob("MSTeams_*"):
            log_dir = pkg / "LocalCache" / "Microsoft" / "MSTeams" / "Logs"
            if log_dir.is_dir():
                return log_dir

        return None

    @staticmethod
    def _find_latest_teams_log(_teams_log_dir) -> Path | None:
        """Return the newest .txt/.log file in the Teams Logs dir, or None."""
        if _teams_log_dir and os.path.exists(_teams_log_dir):
            log_dir = _teams_log_dir
        else:
            log_dir = MSTeamsStatusAPI._find_teams_log_dir()
        if not log_dir:
            return None

        logs = [p for p in log_dir.glob("MSTeams_*.log") if p.is_file()]
        if not logs:
            return None

        return max(logs, key=lambda p: p.stat().st_mtime)

    @staticmethod
    def _tail_lines(path: Path, max_lines: int, block_size: int = 65536) -> list[str]:
        """Last `max_lines` lines of `path`, read from the end without loading the file."""
        blocks: list[bytes] = []
        newlines = 0
        with open(path, "rb") as f:
            f.seek(0, os.SEEK_END)
            pos = f.tell()
            while pos > 0 and newlines <= max_lines:
                read_size = min(block_size, pos)
                pos -= read_size
                f.seek(pos)
                block = f.read(read_size)
                newlines += block.count(b"\n")
                blocks.append(block)
        # Join before decoding so a multi-byte char split across a block boundary survives.
        lines = b"".join(reversed(blocks)).decode("utf-8", errors="replace").splitlines()
        return lines[-max_lines:]
