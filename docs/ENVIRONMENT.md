# Environment notes

## Offline validation (Python 3.13 / Windows, macOS, Linux)

Install FFmpeg / FFprobe into PATH and run:

```bash
python -m unittest discover -s tests -v
python -m src.video_info demo/assessment_stream.mp4 --output outputs/source_info.json
python -m src.video_info demo/carros.mp4 --output outputs/result_info.json
python -m src.create_report
python -m src.assessment_answers
```

No GPU is required for these commands.

## GPU inference (historical NVIDIA DLI DeepStream pipeline)

The reconstructed pipeline uses `Gst` / `pyds`, which require a *compatible* Linux DeepStream environment. It does not run inside a normal Windows Python 3.13 venv. NVIDIA's DeepStream Python bindings for its 9.0 release target Ubuntu 24.04 with Python 3.12, and their use has been deprecated in favor of PyServiceMaker.

1. Install a DeepStream + Gst Python + pyds combination supported together.
2. Download **DashCamNet pruned_v1.0** using the official NGC catalog; place its encrypted model and labels in `models/dashcamnet` and update configuration paths.
3. Verify GStreamer `nvinfer`, `nvdsosd`, `nvv4l2decoder`, `avenc_mpeg4`, `nvvideoconvert` and `nvstreammux` plugins are available.
4. Execute from the repository root:

```bash
python -m src.deepstream_infer \
  --input demo/assessment_stream.h264 \
  --config configs/dashcamnet.txt \
  --output outputs/annotated.mpeg4 \
  --log outputs/tailgating_flags.txt

ffmpeg -y -i outputs/annotated.mpeg4 outputs/annotated.mp4
python -m src.analyze_log outputs/tailgating_flags.txt --fps 59.94005994
python -m src.create_report --log outputs/tailgating_flags.txt
python -m src.assessment_answers --log outputs/tailgating_flags.txt
```

**Compatibility warning:** Legacy `nvinfer` ETLT format and parser settings may not load in modern TensorRT; the GStreamer pipeline is reconstructed but has **not** been GPU-tested. Re-export a compatible model or port to modern APIs as needed. Do not claim fresh inferencing unless successful.
