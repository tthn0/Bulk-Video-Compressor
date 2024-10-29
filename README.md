# Bulk Video Compressor

### Todo

- [ ] The `time_function` decorator isn't outputting anything.
- [ ] Dynamically list out all available video presets based on the files in the config directory.
- [ ] Explore why the timestamp of compressed videos isn't displaying correctly when sent to iPhone via AirDrop.

### Usage

1. Drop the videos you want to compress into the `./src/io/input` directory.
2. Run `python3 ./src/main.py`.
3. Run `tail -n 20 -f src/io/log/log.log` in a separate terminal to monitor log output.
4. The newly compressed videos will be saved in the `./src/io/output` directory.
5. Make sure to check the logs in the `./src/io/logs` directory.

### Dependencies

- FFmpeg
- Python 3.9+

### ChatGPT prompt

> Write a well-structured, object oriented python script that does the provided command to every video file in a directory. The output video should have the same name and extension as the original. It should run the command in parallel to process multiple files at a time. Customizable options:
>
> - Log Directory
> - Input Directory
> - Output Directory
> - CRF
> - Max Frame Rate
> - Max Dimension

### Original commands

##### Compression

```bash
ffmpeg -i in.mov \
  -c:v libx265 \
  -tag:v hvc1 \
  -crf 28 \
  -r 24 \
  -vf "scale='if(gt(max(iw,ih),1440),if(gt(iw,ih),1440,-2),iw)':'if(gt(max(iw,ih),1440),if(gt(ih,iw),1440,-2),ih)'" \
  -map_metadata 0 \
  out.mov
```

- `-c:v libx265`: Video codec (H.265).
- `-tag:v hvc1`: Tag needed for Apple devices.
- `-crf`: Constant rate factor (quality).
- `-r`: Frame rate.
  - This sets the frame rate regardless of the input frame rate.
  - The script will dynamically grab the frame rate from the input and use it.
  - If the `max_frame_rate` parameter is larger than the input frame rate, the original frame rate will (approximately) be preserved.
  - If the `max_frame_rate` parameter is smaller than the input frame rate, the `max_frame_rate` parameter will be used to cap the frame rate of the output video.
- `-vf "scale='if(gt(max(iw,ih),1440),if(gt(iw,ih),1440,-2),iw)':'if(gt(max(iw,ih),1440),if(gt(ih,iw),1440,-2),ih)'"`:
  - If the maximum dimension of the video is > 1440, scale down the entire video whilst preserving the aspect ratio.
  - If the maximum dimension of the video is ≤ 1440, keep the output video dimensino the same.
- `-map_metadata 0`: Copy all metadata (and thus preserve dates).

##### Get framerate

```bash
ffprobe -v error \
  -select_streams v:0 \
  -show_entries stream=r_frame_rate \
  -of default=noprint_wrappers=1:nokey=1 \
  in.mp4
```

### Notes

##### File extensions

- File extensions that are acknowledged in this script are defined in `src/utils/constants.py`.

##### CRF

- **Constant Rate Factor**: a quality-based variable bitrate, typically ∈ [0, 51].
- `0`: **Lossless**. Output is identical to the input, but the file size will be very large.
- `18`: **Visually lossless**. Good for high-quality archival.
- `20-23`: **Good balance**. Used for general-purpose encoding.
- `24-28`: **More compression**. Good for streaming or where file size is a priority.
- `51`: **Worst quality**. Results in the smallest file size.

##### Parallel processing

- Which is the best to use?
  - `concurrent.futures`.
  - `multiprocessing`.
  - `subprocess`.
  - `threading`.
- ChatGPT determined that `concurrent.futures` was the best choice for this task.
- The formula used to determine the amount of parallel workers in this script is `max(1, cpu_count // 2 - 1)` and is guaranteed to be ≥ 1.
