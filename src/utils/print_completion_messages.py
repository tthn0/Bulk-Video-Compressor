from logging import Logger
from pathlib import Path

from utils.constants import CONSTANTS


class COLOR:
    RED: str = "\033[31m"
    YELLOW: str = "\033[33m"
    GREEN: str = "\033[32m"
    RESET: str = "\033[0m"


def format_size(bytes: int) -> str:
    if bytes < 1024:
        return f"{bytes} bytes"
    elif bytes < 1024**2:
        return f"{bytes / 1024:.2f} KB"
    elif bytes < 1024**3:
        return f"{bytes / (1024**2):.2f} MB"
    return f"{bytes / (1024**3):.2f} GB"


def get_size_and_color(original_size: int, new_size: int) -> tuple[str, float]:
    percent_change: float = ((new_size - original_size) / original_size) * 100
    color: str = COLOR.GREEN if percent_change < 0 else COLOR.RED
    return color, percent_change


def get_file_stats(logger: Logger, input_file: Path, output_file: Path) -> None:
    if not output_file.is_file():
        message: str = f"{output_file.name} not found in output directory"
        print(f"{COLOR.YELLOW}{message}{COLOR.RESET}")
        logger.warning(msg=message)
        return

    original_size: int = input_file.stat().st_size
    new_size: int = output_file.stat().st_size
    color, percent_change = get_size_and_color(
        original_size=original_size, new_size=new_size
    )

    message: str = (
        f"{input_file.name} | {format_size(bytes=original_size)} ↦ {format_size(bytes=new_size)} ({percent_change:.2f}%)"
    )
    print(f"{color}{message}")
    logger.info(msg=message)


def compare_video_sizes(logger: Logger, input_dir: Path, output_dir: Path) -> None:
    video_files: list[Path] = [
        file
        for ext in CONSTANTS.VIDEO_EXTENSIONS
        for file in input_dir.glob(pattern=ext)
    ]

    for input_file in sorted(video_files):
        if not input_file.is_file():
            continue

        output_file: Path = output_dir / input_file.name
        get_file_stats(logger=logger, input_file=input_file, output_file=output_file)

    print(COLOR.RESET)


def print_checklist() -> None:
    checklist_items: list[str] = [
        "Logs.",
        "Video frame rate is correct.",
        "Video dimensions are correct.",
        "Video size is actually smaller.",
        "Video is able to be previewed.",
        "Video quality is visually acceptable.",
        "Audio is still working.",
        "Date/timestamp is preserved.",
    ]

    print(COLOR.YELLOW)
    print("Checklist:")
    for item in checklist_items:
        print(f"- {item}")
    print(COLOR.RESET)


def print_completion_messages(logger: Logger) -> None:
    input_dir: Path = CONSTANTS.SRC_DIR / "io" / "input"
    output_dir: Path = CONSTANTS.SRC_DIR / "io" / "output"

    print_checklist()
    compare_video_sizes(logger=logger, input_dir=input_dir, output_dir=output_dir)
