import logging
import os
import subprocess
from concurrent.futures import Future, ProcessPoolExecutor
from logging import Logger
from pathlib import Path

from utils.constants import CONSTANTS
from utils.time_function import time_function


class VideoCompressor:
    """A class to compress video files using FFmpeg."""

    def __init__(
        self,
        logger: Logger,
        input_dir: Path,
        output_dir: Path,
        crf: int = 28,
        max_frame_rate: int = 24,
        max_dimension: int = 1440,
    ) -> None:
        """
        Initializes the VideoCompressor with the specified parameters.

        Args:
            input_dir (str): Path to the input directory.
            output_dir (str): Path to the output directory.
            crf (int, optional): CRF value for quality. Defaults to 26.
            max_frame_rate (int, optional): Frame rate for the output video. Defaults to 30.
            max_dimension (int, optional): Maximum pixel dimension. Defaults to 1600.
        """

        self.logger: Logger = logger
        self.input_dir: Path = input_dir
        self.output_dir: Path = output_dir
        self.crf: int = crf
        self.max_frame_rate: int = max_frame_rate
        self.max_dimension: int = max_dimension

        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger.info(
            msg=f"Initialized VideoCompressor with input_dir='{self.input_dir}' and output_dir='{self.output_dir}'."
        )

    def determine_frame_rate(self, input_file: Path) -> float:
        """Checks the frame rate of a video file and determines the frame rate to use."""

        probe_command: list[str] = [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=r_frame_rate",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(input_file),
        ]

        try:
            original_frame_rate: str = (
                subprocess.check_output(args=probe_command).decode().strip()
            )
            # Convert the frame rate (e.g., "30/1" or "30000/1001") to float
            num, denom = map(int, original_frame_rate.split(sep="/"))
            original_frame_rate_float: float = num / denom
        except Exception as e:
            self.logger.error(
                msg=f"Could not determine frame rate for {input_file.name}. Using max framerate parameter instead. {e}"
            )
            return self.max_frame_rate

        frame_rate_to_use: float = min(original_frame_rate_float, self.max_frame_rate)
        return round(
            number=frame_rate_to_use,
            ndigits=2,
        )

    def compress_video(self, input_file: Path) -> None:
        """
        Compresses a single video file using FFmpeg.

        Args:
            input_file (Path): The input video file to be compressed.
        """

        output_file: Path = self.output_dir / input_file.name
        command: list[str] = [
            "ffmpeg",
            "-i",
            str(input_file),
            "-c:v",
            "libx265",
            "-tag:v",
            "hvc1",
            "-crf",
            str(self.crf),
            "-r",
            str(self.determine_frame_rate(input_file=input_file)),
            "-vf",
            f"scale='if(gt(max(iw,ih),{self.max_dimension}),if(gt(iw,ih),{self.max_dimension},-2),iw)':'if(gt(max(iw,ih),{self.max_dimension}),if(gt(ih,iw),{self.max_dimension},-2),ih)'",
            "-map_metadata",
            "0",
            str(output_file),
        ]

        self.logger.info(
            msg=f"Starting compression for {input_file} to {output_file}..."
        )

        try:
            subprocess.run(args=command, check=True)
            self.logger.info(
                msg=f"Successfully compressed {input_file} to {output_file}"
            )
        except subprocess.CalledProcessError as e:
            self.logger.error(msg=f"Failed to compress {input_file.name}: {e}")

    def determine_max_workers(self) -> int:
        """Determines the number of workers to be used for parallel processing."""

        cpu_count: int | None = os.cpu_count()
        max_workers: int = max(1, cpu_count // 2 - 1) if cpu_count else 1

        if cpu_count:
            self.logger.info(
                msg=f"Detected {cpu_count} CPUs, using {max_workers} workers."
            )
        else:
            self.logger.warning(
                msg="Could not determine CPU count, defaulting to 1 worker."
            )
        return max_workers

    @time_function(logger=logging.getLogger(name=__name__))
    def compress_all_videos_parallel(self) -> None:
        """
        Compresses all video files in the input directory in parallel.
        Supported formats are listed in `constants.py`.
        """
        video_files: list[Path] = [
            file
            for ext in CONSTANTS.VIDEO_EXTENSIONS
            for file in self.input_dir.glob(pattern=ext)
            if not (
                self.output_dir / file.name
            ).is_file()  # Skip files that are already in the output directory
        ]

        if not video_files:
            self.logger.warning(
                msg="No video files found in the input directory that aren't already in output directory."
            )
            return

        self.logger.info(
            msg=f"Found {len(video_files)} video files to compress: "
            + repr([file.name for file in video_files])
        )

        max_workers: int = self.determine_max_workers()
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures: dict[Future[None], Path] = {
                executor.submit(self.compress_video, video_file): video_file
                for video_file in video_files
            }
            for future in futures:
                try:
                    future.result()  # Will raise an exception if the conversion failed
                except Exception as e:
                    self.logger.error(
                        msg=f"Error compressing {futures[future].name}: {e}"
                    )

        self.logger.info(msg="Parallel conversion completed for all videos.")
