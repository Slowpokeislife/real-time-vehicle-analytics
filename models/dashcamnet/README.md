# NVIDIA DashCamNet weights (not redistributed)

Obtain the official pruned_v1.0 DashCamNet model using NVIDIA NGC's model catalog:
https://catalog.ngc.nvidia.com/orgs/nvidia/tao/models/dashcamnet/pruned_v1.0

Historical training environment command:

```bash
ngc registry model download-version nvidia/tao/dashcamnet:pruned_v1.0 --dest models
```

Locate the downloaded `.etlt` and model label file, then update the exact paths
in `configs/dashcamnet.txt`. TensorRT engines are architecture/version-dependent
and should be rebuilt on target hardware. NVIDIA's encoded model key is
`tlt_encode` according to its model card. Do not publish any downloaded model
artifacts without checking the applicable NVIDIA terms.
