from pathlib import Path


class CONSTANTS:
    SRC_DIR: Path = Path(__file__).parent.parent
    VIDEO_EXTENSIONS: tuple[str, ...] = ("*.mp4", "*.MP4", "*.mov", "*.MOV")
