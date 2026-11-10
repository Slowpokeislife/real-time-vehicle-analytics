# AI-Powered Tailgating Detection

**NVIDIA DeepStream · TAO Toolkit / DashCamNet · GStreamer · Python · Video Analytics**

A **portfolio reconstruction** of my NVIDIA Deep Learning Institute assessment on dashcam-based vehicle proximity monitoring. The task was to build a DeepStream pipeline that detects cars and flags frames where a vehicle's bounding box suggests possible following at close visual proximity. The repository retains the original/annotated demo and adds readable source, tests, evidence-aware analysis and a generated technical report.

> **Important:** The video demo was created in the course environment. The reconstructed GPU pipeline has **not** been run again on a compatible system. The binary tailgating log from the course submission was not recovered; therefore, this README does not claim measured tailgating rates.

## Real-world comparison

| Original dashcam feed | Annotated result |
|---|---|
| ![Original frame](assets/original.jpg) | ![Annotated detections](assets/result.jpg) |
| [Original stream](demo/assessment_stream.mp4) | [Annotated demo](demo/carros.mp4) |

Open [`demo/index.html`](demo/index.html) locally to compare both recordings side by side. Browser playback supports MP4.

## Problem and approach

The assessment simulates a fleet safety analytics scenario: find frames that might indicate a vehicle following another vehicle too closely. It uses NVIDIA **DashCamNet** (`pruned_v1.0`) for object detection, DeepStream / GStreamer for accelerated video processing, and a metadata pad probe for per-frame event logging.

```text
Dashcam (.h264)
      |
 filesrc → h264parse → nvv4l2decoder → nvstreammux
      |
   nvinfer (DashCamNet)
      |
   nvdsosd + pad probe ───────→ 0/1 indicator per frame
      |                                 |
 nvvideoconvert → encoder             event summaries
      |
  annotated video
```

For car bounding boxes, a **potential** tailgating signal is raised if:

```python
box.width > 0.30 * frame_width and (box.top + box.height) > 0.90 * frame_height
```

Frames get exactly **one** 0/1 flag, even if several vehicles are detected. This is a spatial heuristic, **not** a measured distance, time-headway or collision prediction. See [`src/tailgating.py`](src/tailgating.py).

## Recovered material and findings

- The recovered assessment was a **NVIDIA DLI assignment** based on DashCamNet, not the traffic camera model used in the earlier generic reconstruction.
- Original `assessment_stream.mp4` and annotated `carros.mp4` have **1280 × 720** resolution, about **59.94 FPS**, **2406 frames** and **40.14 s** duration.
- The video demo visually shows red detection boxes labeled `car`.
- The submission notebook still had `FIXME` placeholders and `my_assessment/answer_*.txt` outputs were empty. The finished submission file and per-frame log were not present in the recovered ZIP.

## Repository

```text
src/
  deepstream_infer.py      # reconstructed legacy GPU pipeline
  tailgating.py           # complete frame-level decision rule
  video_info.py           # ffprobe inspection
  analyze_log.py          # timeline and event statistics
  create_report.py        # generates technical report
  assessment_answers.py   # reconstructs available assessment artifacts
configs/dashcamnet.txt     # corrected config template for NGC model
demo/                      # original + annotated videos; browser comparison
assets/                    # screenshots, source assessment diagrams
reports/TECHNICAL_REPORT.md
docs/ENVIRONMENT.md        # exact commands and compatibility caveats
docs/PROVENANCE.md         # what is recovered vs reconstructed
tests/                     # small unit test suite
models/dashcamnet/         # weights intentionally excluded
```

## Run offline tools (Windows + Python 3.13 OK)

Install [FFmpeg](https://ffmpeg.org/) so `ffprobe` is available, then:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m unittest discover -s tests -v
python -m src.video_info demo/assessment_stream.mp4 --output outputs/source.json
python -m src.video_info demo/carros.mp4 --output outputs/annotated.json
python -m src.create_report
```

## Execute inference on GPU

See [environment and exact pipeline commands](docs/ENVIRONMENT.md). This step requires Linux + compatible NVIDIA DeepStream / GStreamer / PyDS and the separately downloaded DashCamNet model. **Do not run the GPU pipeline in a Windows Python 3.13 venv.** A modern DeepStream deployment may require model conversion and an updated inference API.

Once an authentic inference log exists:

```bash
python -m src.analyze_log outputs/tailgating_flags.txt --fps 59.94005994
python -m src.create_report --log outputs/tailgating_flags.txt
```

This then produces quantitative summaries, contiguous episodes, and a refreshed report. Without the log, the report intentionally displays *unavailable* rather than invented results.

## Project report

[Read the full technical report](reports/TECHNICAL_REPORT.md), automatically generated using `ffprobe` metadata. It includes the problem, methods, frames, source/annotated comparison, limitations, reproducibility and learning outcomes.

## What I learned

- Connecting GStreamer components into a DeepStream pipeline.
- Configuring TAO pretrained models for `nvinfer` detection.
- Reading object metadata from DeepStream pad probes.
- Turning object-level detections into per-frame event signals.
- Documenting reproducibility, model provenance and deployment limitations.

## Attribution and licensing

This portfolio project was developed from an NVIDIA DLI educational assessment and NVIDIA technologies. NVIDIA and its respective licensors retain rights to their training material, pretrained models and applicable assets. The completed original submission was not recovered; code in `src/` is a new reconstruction. Video redistribution is subject to authorization; review before publication. [Details](docs/PROVENANCE.md).

## References

- [NVIDIA DashCamNet](https://catalog.ngc.nvidia.com/orgs/nvidia/tao/models/dashcamnet)
- [NVIDIA DeepStream SDK](https://docs.nvidia.com/deepstream/)
- [DeepStream Python Apps](https://github.com/NVIDIA-AI-IOT/deepstream_python_apps)
