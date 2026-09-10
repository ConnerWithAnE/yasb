import logging
import re

from core.utils.tooltip import set_tooltip
from core.utils.utilities import refresh_widget_style
from core.validation.widgets.yasb.ms_teams_status import MSTeamsStatusConfig
from core.widgets.base import BaseWidget
from core.widgets.services.ms_teams_status.ms_teams_status_api import MSTeamsStatusAPI


class MSTeamsStatusWidget(BaseWidget):
    validation_schema = MSTeamsStatusConfig

    _instance: list[MSTeamsStatusWidget] = []

    def __init__(self, config: MSTeamsStatusConfig):
        super().__init__(config.update_interval, class_name=f"ms-teams-status-widget {config.class_name}")
        self.config = config
        self._show_alt_label = False

        self._label_content = config.label
        self._label_alt_content = config.label_alt

        self._teams_api = MSTeamsStatusAPI.get_instance(self)

        self._init_container()
        self.build_widget_label(self.config.label, self.config.label_alt)
        self.register_callback("update_label", self._update_label)
        self.register_callback("toggle_label", self._toggle_label)
        self.callback_left = config.callbacks.on_left
        self.callback_right = config.callbacks.on_right
        self.callback_timer = "update_label"
        self.start_timer()

    def _toggle_label(self):
        self._show_alt_label = not self._show_alt_label
        for widget in self._widgets:
            widget.setVisible(not self._show_alt_label)
        for widget in self._widgets_alt:
            widget.setVisible(self._show_alt_label)
        self._update_label()

    def _update_label(self):  # , status: AvailabilityStatus):
        self.teams_status = self._teams_api.get_status()
        dot_colour = getattr(self.config.status_colours, (self.teams_status.status_class.value).replace("-", "_"))

        ms_teams_data = {
            "{dot}": f'<span style="color:{dot_colour}">{self.teams_status.dot.value}</span>',
            "{status_text}": self.teams_status.status.value,
            "{unread_notifs}": self.teams_status.unread,
        }

        active_widgets = self._show_alt_label and self._widgets_alt or self._widgets
        active_label_content = self._show_alt_label and self._label_alt_content or self._label_content
        label_parts = re.split(r"(<span.*?>.*?</span>)", active_label_content)
        label_parts = [part for part in label_parts if part]

        if self.config.tooltip:
            tooltip = f"<strong>{self.teams_status.status.value}</strong>"
            set_tooltip(self, tooltip)

        widget_index = 0

        try:
            for part in label_parts:
                part = part.strip()
                # Decide icon vs label from the template, before substitution —
                # substituted values may themselves contain <span> markup.
                is_icon = "<span" in part and "</span>" in part
                for option, value in ms_teams_data.items():
                    part = part.replace(option, str(value))
                if not part or widget_index >= len(active_widgets):
                    continue
                if is_icon:
                    icon = re.sub(r"<span.*?>|</span>", "", part).strip()
                    active_widgets[widget_index].setText(icon)
                else:
                    label_class = "label alt" if self._show_alt_label else "label"
                    formatted_text = part.format(info=ms_teams_data)
                    active_widgets[widget_index].setText(formatted_text)
                    new_class = f"{label_class} status-{self.teams_status.status_class.value}"
                    if active_widgets[widget_index].property("class") != new_class:
                        active_widgets[widget_index].setProperty("class", new_class)
                        refresh_widget_style(active_widgets[widget_index])
                widget_index += 1
        except Exception as e:
            logging.exception("Failed to update label: %s", e)
