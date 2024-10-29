from logging import Logger
from pathlib import Path

from utils import (
    CONSTANTS,
    Config,
    VideoCompressor,
    create_logger,
    print_completion_messages,
)


def main() -> None:
    log_dir: Path = CONSTANTS.SRC_DIR / "io" / "log"
    input_dir: Path = CONSTANTS.SRC_DIR / "io" / "input"
    output_dir: Path = CONSTANTS.SRC_DIR / "io" / "output"

    logger: Logger = create_logger(log_dir=log_dir)
    config: Config = Config(config_preset=Config.ask_for_preset())

    compressor: VideoCompressor = VideoCompressor(
        logger=logger,
        input_dir=input_dir,
        output_dir=output_dir,
        crf=config.crf,
        max_frame_rate=config.max_frame_rate,
        max_dimension=config.max_dimension,
    )
    compressor.compress_all_videos_parallel()
    print_completion_messages(logger=logger)


if __name__ == "__main__":
    main()
