from typing import Literal

from pydantic import Field

from core.validation.widgets.base_model import CallbacksConfig, CustomBaseModel


class MSTeamsStatusCardConfig(CustomBaseModel):
    blur: bool = True
    round_corners: bool = True
    round_corners_type: Literal["normal", "small"] = "normal"
    border_color: str = "System"
    alignment: str = "right"
    direction: str = "down"
    offset_top: int = 6
    offset_left: int = 0
    columns: int = 1
    reset_icon: str = "\u25cb"
    reset_icon_colour: str = "#8A8886"


class MSTeamsStatusColoursConfig(CustomBaseModel):
    available: str = "#92C353"
    available_idle: str = "#92C353"
    away: str = "#F8D22A"
    be_right_back: str = "#F8D22A"
    busy: str = "#C4314B"
    in_a_meeting: str = "#C4314B"
    in_a_call: str = "#C4314B"
    presenting: str = "#C4314B"
    on_the_phone: str = "#C4314B"
    do_not_disturb: str = "#C4314B"
    focusing: str = "#C4314B"
    offline: str = "#8A8886"


class MSTeamsStatusIconConfig(CustomBaseModel):
    available: str = "\u25cf"
    available_idle: str = "\u25cf"
    away: str = "\u25cf"
    be_right_back: str = "\u25cf"
    busy: str = "\u25cf"
    in_a_meeting: str = "\u25cf"
    in_a_call: str = "\u25cf"
    presenting: str = "\u25cf"
    on_the_phone: str = "\u25cf"
    do_not_disturb: str = "\u2296"
    focusing: str = "\u2296"
    offline: str = "\u25cb"


class CallbacksMSTeamsStatusConfig(CallbacksConfig):
    on_left: str = "toggle_label"
    on_right: str = "toggle_label"


class MSTeamsStatusConfig(CustomBaseModel):
    label: str = "{data[html]}"
    label_alt: str = "{data[html]} {data[text]}"
    class_name: str = "ms_teams_status"
    update_interval: int = Field(default=10000, ge=1000, le=60000)
    logs_path: str = "$env:LOCALAPPDATA/Packages/MSTeams_*/LocalCache/Microsoft/MSTeams/Logs/MSTeams_*.log"
    tooltip: bool = True
    callbacks: CallbacksConfig = CallbacksMSTeamsStatusConfig()
    status_colours: MSTeamsStatusColoursConfig = MSTeamsStatusColoursConfig()
    status_icons: MSTeamsStatusIconConfig = MSTeamsStatusIconConfig()
    status_card: MSTeamsStatusCardConfig = MSTeamsStatusCardConfig()
