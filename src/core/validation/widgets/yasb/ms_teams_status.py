from pydantic import Field

from core.validation.widgets.base_model import CallbacksConfig, CustomBaseModel


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


class CallbacksMSTeamsStatusConfig(CallbacksConfig):
    on_left: str = "toggle_label"
    on_right: str = "toggle_label"


class MSTeamsStatusConfig(CustomBaseModel):
    label: str = "{data[html]}"
    label_alt: str = "{data[html]} {data[text]}"
    class_name: str = "ms_teams_status"
    update_interval: int = (Field(default=10000, ge=1000, le=60000),)
    logs_path: str = "$env:LOCALAPPDATA/Packages/MSTeams_*/LocalCache/Microsoft/MSTeams/Logs/MSTeams_*.log"
    tooltip: bool = True
    callbacks: CallbacksConfig = CallbacksMSTeamsStatusConfig()
    status_colours: MSTeamsStatusColoursConfig = MSTeamsStatusColoursConfig()
