# Basler Camera Setup

This directory contains the first camera detection probe for a Basler ace 2 USB3 Vision camera.

## What was wrong

The camera was visible inside WSL with `lsusb`:

```text
2676:ba05 Basler AG Vision Camera
```

Windows also showed the camera attached to WSL through `usbipd`:

```text
2676:ba05 Basler ace 2 USB3 Vision Camera  Attached
```

There were two separate issues during setup:

1. `sudo python3 setup.py` used the system Python. It did not use the active virtual environment, so it failed with:

   ```text
   ModuleNotFoundError: No module named 'pypylon'
   ```

   `sudo` does not automatically preserve the virtual environment.

2. The USB device initially had restrictive permissions:

   ```text
   crw-rw-r-- 1 root root /dev/bus/usb/002/002
   ```

   The normal user could not access the camera through pylon. After the udev rule was applied and the camera reconnected, the device permissions became:

   ```text
   crw-rw-rw- 1 root root /dev/bus/usb/002/003
   ```

   The USB device number can change after reconnecting; do not hardcode it.

## Clean setup

### 1. Install WSL USB support on Windows

Run PowerShell as Administrator:

```powershell
winget install --interactive --exact dorssel.usbipd-win
```

List USB devices:

```powershell
usbipd list
```

Find the Basler bus ID, then bind and attach it:

```powershell
usbipd bind --busid <BUSID>
usbipd attach --wsl --busid <BUSID>
```

For example, the Basler device may appear as bus ID `2-19`. The bus ID is not guaranteed to remain the same.

To reconnect it later:

```powershell
usbipd detach --busid <BUSID>
usbipd attach --wsl --busid <BUSID>
```

Close Windows applications such as Basler pylon Viewer before attaching the camera to WSL.

### 2. Create a clean Python environment in WSL

From this directory:

```bash
cd ~/Desktop/Quality-Control-OCP/cam

rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Verify that Python and pypylon come from the environment:

```bash
which python
python -m pip show pypylon
python -c "import pypylon; print(pypylon.__file__)"
```

Use `python -m pip`, not a separate `pip3`, so packages are installed into the interpreter that runs the program.

### 3. Allow the normal WSL user to access the camera

Create a udev rule inside WSL:

```bash
sudo tee /etc/udev/rules.d/99-basler-camera.rules >/dev/null <<'EOF'
SUBSYSTEM=="usb", ATTR{idVendor}=="2676", MODE="0666"
EOF

sudo udevadm control --reload-rules
sudo udevadm trigger
```

Reconnect the camera from Administrator PowerShell after changing the rule:

```powershell
usbipd detach --busid <BUSID>
usbipd attach --wsl --busid <BUSID>
```

Check the new device node in WSL:

```bash
lsusb
ls -l /dev/bus/usb/*/*
```

The Basler device should be readable and writable by the current user. The bus and device numbers may change after reconnecting.

### 4. Run the probe

With the environment activated:

```bash
source .venv/bin/activate
python setup.py
```

The expected result is similar to:

```text
Python: .../cam/.venv/bin/python
Detected cameras: 1
- Basler ...
```

The Makefile can also be used:

```bash
make run
```

Do not normally run the probe with `sudo`. If a privileged comparison is needed, use the virtual environment's interpreter explicitly:

```bash
sudo "$VIRTUAL_ENV/bin/python" setup.py
```

Using `sudo python3 setup.py` runs the system interpreter and can produce `ModuleNotFoundError` even when `pypylon` is installed in `.venv`.

## Troubleshooting

### WSL cannot see the camera

In Windows PowerShell:

```powershell
usbipd list
```

The Basler camera must show `Attached`. In WSL:

```bash
lsusb
```

The camera should show vendor ID `2676` and product ID `ba05`.

### `pypylon` imports but detects zero cameras

Check that the USB transport library is installed:

```bash
find .venv -name 'libpylon_TL_usb.so*' -o -name '*pylon*usb*.so*'
```

Check the camera permissions:

```bash
ls -l /dev/bus/usb/*/*
```

If the device is still owned by `root` with permissions such as `crw-rw-r--`, reload the udev rule and reconnect the camera.

### The Python executable is unexpected

Run:

```bash
which python
python -c "import sys; print(sys.executable)"
python -c "import pypylon; print(pypylon.__file__)"
```

The paths should point into the project `.venv`. Activate it again if necessary:

```bash
source .venv/bin/activate
```

### USAGE
    refer to the official documentation of pylon for pypylon 