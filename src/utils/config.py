from __future__ import annotations

import json
from enum import Enum
from pathlib import Path

from utils.constants import CONSTANTS


class Config:
    class Preset(Enum):
        LOW = "low_quality.json"
        MEDIUM = "medium_quality.json"
        HIGH = "high_quality.json"
        CUSTOM = "custom_quality.json"

    @staticmethod
    def ask_for_preset() -> Config.Preset:
        choice: None | Config.Preset = None

        while choice is None:
            options: str = ", ".join(preset.name for preset in Config.Preset)
            prompt: str = f"Choose preset ({options}): "
            user_input: str = input(prompt).strip().upper()
            try:
                choice = Config.Preset[user_input]
            except KeyError:
                print("Invalid choice.")

        return choice

    def __init__(self, config_preset: Config.Preset) -> None:
        config_file: Path = CONSTANTS.SRC_DIR / "config" / config_preset.value

        with open(file=config_file, mode="r") as f:
            config: dict[str, int] = json.load(fp=f)
            self.crf: int = config["crf"]
            self.max_frame_rate: int = config["max_frame_rate"]
            self.max_dimension: int = config["max_dimension"]
