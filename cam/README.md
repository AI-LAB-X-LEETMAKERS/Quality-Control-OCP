# Basler Camera Probe

This directory contains a small pypylon probe for detecting a Basler camera and
capturing a fixed set of images.

## Requirements

Install Python 3, `make`, and the packages listed in `requirements.txt`:

- `pypylon`
- `numpy`
- `opencv-python`

The camera must be available to pypylon before running the probe.

## Workflow

Run these commands from this directory:

```bash
make build
make run
```

`make build` installs the Python dependencies with:

```bash
pip3 install -r requirements.txt
```

`make run` executes:

```bash
python3 setup.py
```

## What `setup.py` does

1. Enumerates connected cameras through the pylon transport-layer factory.
2. Prints the friendly name and serial number of the first camera.
3. Opens the first available camera.
4. Grabs up to 30 images using the `GrabStrategy_OneByOne` strategy.
5. Saves each image as a PNG in the `output` directory.

The generated files are named `output/image1.png` through `output/image30.png`.
The actual number of files depends on whether grabbing succeeds for all 30
frames.

To remove generated images, run:

```bash
make clean
```

This removes files matching `output/image*`.

## Reference

See the official [pypylon documentation](https://docs.baslerweb.com/pypylon-introduction.html)
for camera discovery, image acquisition, and result handling.