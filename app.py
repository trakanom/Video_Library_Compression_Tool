import os
import sys
import time
import logging
import subprocess
from pathlib import Path
from tqdm import tqdm
import subprocess
import re
import asyncio
import atexit
from tabulate import tabulate
from datetime import timedelta

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class VideoCompressor:
    def __init__(self, directory, crf=20, overwrite_original=False):
        self.directory = Path(directory)
        self.crf = crf
        self.overwrite_original = overwrite_original
        self.extensions = {".mkv", ".mp4", ".avi"}
        self.total_space_saved = 0
        self.total_files_compressed = 0
        self.file_stats = []

    # def get_video_files(self):
    #     video_files = [
    #         path
    #         for path in self.directory.rglob("*")
    #         if path.is_file()
    #         and path.suffix.lower() in self.extensions
    #         and not path.name.endswith(".compressed.mkv")
    #     ]
    #     return video_files

    def get_video_files(self):
        video_files = [
            path
            for path in self.directory.rglob("*")
            if path.is_file()
            and path.suffix.lower() in self.extensions
            and not path.name.endswith(".compressed.mkv")
        ]

        # Calculate bit rate density and file size for each video file
        video_files_info = []
        for video_file in video_files:
            size = video_file.stat().st_size
            duration = self.get_video_duration(video_file)
            bit_rate_density = size / duration if duration else 0
            video_files_info.append((video_file, bit_rate_density, size))

        # Sort by bit rate density (descending) and then by file size (ascending)
        video_files_info.sort(key=lambda x: (-x[1], x[2]))

        # Output the sorted list
        for video_file, bit_rate_density, size in video_files_info:
            print(
                f"File: {video_file}, Bit Rate Density: {bit_rate_density}, Size: {size}"
            )

        # Return sorted list of video files
        return [video_file for video_file, _, _ in video_files_info]

    def get_video_duration(self, input_file):
        command = [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(input_file),
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        duration_match = re.search(r"(\d+\.\d+)", result.stdout)
        if duration_match:
            return float(duration_match.group(1))
        else:
            logging.error(
                f"Could not extract duration from ffprobe output: {result.stdout}"
            )
            return 0

    def time_to_seconds(self, time_str):
        h, m, s = map(float, time_str.split(":"))
        return h * 3600 + m * 60 + s

    async def compress_video_file(self, input_file, output_file):
        command = [
            "ffmpeg",
            "-i",
            str(input_file),
            "-c:v",
            # "libx265", #CRF of 24
            "hevc_nvenc",  # Use Nvidia's HEVC encoder # CQP of 20
            "-crf",
            str(self.crf),
            "-c:a",
            "copy",
            "-hide_banner",
            "-y",
            str(output_file),
        ]

        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )

        return process

    async def monitor_progress(self, process, input_file, pbar):
        duration = self.get_video_duration(input_file)
        pattern = re.compile(r"time=(\d+:\d+:\d+.\d+)")

        while process.returncode is None:
            # Changed readline to read, which does not look for a newline character
            # and does not raise LimitOverrunError
            line = await process.stdout.read(100)  # read 100 bytes at a time
            line = line.decode().strip()
            match = pattern.search(line)
            if match:
                time = self.time_to_seconds(match.group(1))
                pbar.update(time / duration * 100)
            await asyncio.sleep(0.1)

        await process.communicate()
        return process.returncode

    async def process_files(self):
        video_files = self.get_video_files()
        # video_files.sort(key=lambda x: x.stat().st_size) # sort by size ascending

        with tqdm(total=len(video_files), unit="bytes") as pbar:
            for input_file in video_files:
                logging.info(f"Processing: {input_file}")
                output_file = input_file.with_suffix(".compressed.mkv")

                if output_file.exists():
                    logging.info(f"File {output_file} already exists. Skipping.")
                    pbar.update()
                    continue

                process = await self.compress_video_file(input_file, output_file)
                return_code = await self.monitor_progress(process, input_file, pbar)

                if return_code == 0:
                    original_size = input_file.stat().st_size
                    compressed_size = output_file.stat().st_size
                    stats = {
                        "name": input_file.name,
                        "duration": self.get_video_duration(input_file),
                        "original_size": original_size,
                        "compressed_size": compressed_size,
                    }
                    self.file_stats.append(stats)

                    # Check size and duration
                    if 0.05 * original_size < compressed_size <= original_size:
                        original_duration = self.get_video_duration(input_file)
                        compressed_duration = self.get_video_duration(output_file)
                        if abs(original_duration - compressed_duration) < 1:
                            if self.overwrite_original:
                                os.remove(input_file)
                                # os.rename(output_file, input_file)
                                self.total_files_compressed += 1
                                self.total_space_saved += (
                                    original_size - compressed_size
                                )
                            else:
                                logging.info(f"Compressed file saved as: {output_file}")
                                self.total_files_compressed += 1
                                self.total_space_saved
                                self.total_space_saved += (
                                    original_size - compressed_size
                                )
                        else:
                            logging.error(
                                f"Durations do not match for {input_file} and {output_file}."
                            )
                            os.remove(output_file)
                    else:
                        logging.error(
                            f"Compressed file size not within expected range for {input_file}. Original: {original_size}, Compressed: {compressed_size}, % Diff: {(original_size-compressed_size)/original_size}"
                        )
                        # os.remove(output_file)
                    pbar.update()
                else:
                    logging.error(
                        f"Error compressing {input_file}. FFmpeg returned {return_code}."
                    )

    def run(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.process_files())
        loop.close()

        logging.info(
            f"Compression completed. {self.total_files_compressed} files were compressed."
        )
        logging.info(
            f"Total space saved: {self.total_space_saved / (1024 ** 3):.2f} GB"
        )

        return self.file_stats


def print_summary():
    total_duration = sum(file["duration"] for file in compressor.file_stats)
    total_original_size = sum(file["original_size"] for file in compressor.file_stats)
    total_compressed_size = sum(
        file["compressed_size"] for file in compressor.file_stats
    )
    print("Total duration compressed:", timedelta(seconds=total_duration))
    print(
        "Total data compressed:", total_original_size - total_compressed_size, "bytes"
    )

    table = tabulate(
        compressor.file_stats,
        headers="keys",
        tablefmt="pipe",
        floatfmt=".2f",
    )
    print(table)


def main():
    directory = input("Enter the directory: ")
    crf = input("Enter the CRF value (0-51): ")
    overwrite_original = (
        input("Do you want to overwrite the original files? (yes/no): ").lower()
        == "yes"
    )
    global compressor
    compressor = VideoCompressor(directory, crf, overwrite_original)
    atexit.register(print_summary)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(compressor.process_files())
    loop.close()


if __name__ == "__main__":
    main()
