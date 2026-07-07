# IPU6 Camera with icamerasrc (GStreamer)

Using the Intel IPU6 MIPI camera (e.g. OV02C10 sensor) via the `icamerasrc` GStreamer plugin and the IPU6 camera HAL.

Tested on a Raptor Lake platform (Core i7-13800H, IPU6 PCI `8086:a75d`, `ipu6ep` config set) with the `ov02c10` sensor and the out-of-tree IPU6 kernel modules (`intel_ipu6`, `intel_ipu6_isys`, `intel_ipu6_psys`).

On this particular laptop, these are the components required to get a full working setup:

- Platform: Raptor Lake i7‑13800H, IPU6 PCI 8086:a75d, uses the `ipu6ep` config set
- Sensor: ov02c10 19-0036 bound to CSI2 port 3 (`[ENABLED,IMMUTABLE]`)
- HAL config: `/usr/share/camera/ipu6ep/` present, incl. `OV02C10_*.aiqb` + `ov02c10-uf.xml`
- Firmware: `ipu6ep_fw.bin` present
- Plugin: `libgsticamerasrc.so`, camera device-name `ov02c10-uf`
- ISYS nodes: `/dev/video*`, `/dev/media2` with `uaccess` ACL for your session
- PSYS node: `/dev/ipu-psys0` with `uaccess` ACL for your session

## Prerequisites

Install the IPU6 stack:

- `ipu6-camera-bins` — firmware plus proprietary binaries.
- `ipu6-camera-hal` — camera HAL and per-platform configs (`/usr/share/camera/`).
- `gstreamer1-plugin-icamerasrc` — the `icamerasrc` GStreamer element.
- `dkms-ipu6` or `akmod-ipu6` — kernel modules including the sensor drivers.

Confirm the sensor is bound in the media graph (should show `[ENABLED,IMMUTABLE]`). For example:

```bash
$ media-ctl -d /dev/media2 -p | grep -i ov02c10
		<- "ov02c10 19-0036":0 [ENABLED,IMMUTABLE]
- entity 248: ov02c10 19-0036 (1 pad, 1 link, 0 routes)
```

### PSYS device permissions

The processing side exposes `/dev/ipu-psys0`, which by default is `crw------- root root` — only root can open it, so pipelines fail with `Failed to open PSYS, error: Permission denied`. Grant the `video` group and a uaccess ACL (matching the ISYS `/dev/video*` nodes) with a udev rule:

```bash
$ cat /usr/lib/udev/rules.d/72-ipu6-psys.rules
SUBSYSTEM=="intel-ipu6-psys", TAG+="uaccess"
```

Verify that the device files have the proper ACL:

```bash
$ getfacl /dev/ipu-psys0
getfacl: Removing leading '/' from absolute path names
# file: dev/ipu-psys0
# owner: root
# group: root
user::rw-
user:slaanesh:rw-
group::---
mask::rw-
other::---
```

## Caps note

This `icamerasrc` build emits **only** DMABuf with a DRM format: `video/x-raw(memory:DMABuf), format=DMA_DRM, drm-format=NV12` (linear).

- Caps filters must use `format=DMA_DRM`; a plain `format=NV12` will not negotiate.
- The buffers are **linear** NV12. `vapostproc` only imports **tiled** NV12 DMABuf, so it will not link directly — route conversions through `glupload` / `gldownload` (GL) instead of VA, as shown below.

## Commands

### Headless sanity check (no display)

```bash
gst-launch-1.0 icamerasrc num-buffers=30 printfps=true ! \
  "video/x-raw(memory:DMABuf),format=DMA_DRM,width=1280,height=720" ! fakesink
```

### Live preview (Wayland/GL, keeps it as DMABuf)

```bash
gst-launch-1.0 icamerasrc ! \
  "video/x-raw(memory:DMABuf),format=DMA_DRM,width=1920,height=1080" ! \
  glimagesink
```

The window opens small; drag to resize or maximize it.

### DMABuf → system-memory NV12

```bash
gst-launch-1.0 icamerasrc ! \
  "video/x-raw(memory:DMABuf),format=DMA_DRM,width=1920,height=1080" ! \
  glupload ! glcolorconvert ! gldownload ! "video/x-raw,format=NV12" ! \
  videoconvert ! autovideosink
```

### Record to H.264 MP4 (encode on the GPU via `vah264enc`, which takes system NV12)

```bash
gst-launch-1.0 -e icamerasrc ! \
  "video/x-raw(memory:DMABuf),format=DMA_DRM,width=1920,height=1080" ! \
  glupload ! glcolorconvert ! gldownload ! "video/x-raw,format=NV12" ! \
  vah264enc ! h264parse ! mp4mux ! filesink location=cam.mp4
```

### Selecting a sensor

There is usually a single camera (the default). To pick one explicitly:

```bash
gst-launch-1.0 icamerasrc device-name=ov02c10-uf ! ...
```

## Use as a standard webcam (v4l2loopback)

`icamerasrc` is a native GStreamer source and does **not** create a `/dev/videoN` node, so apps expecting a plain webcam (browsers, conferencing apps, `v4l2src`) cannot use it directly. Bridge it through `v4l2loopback`: a GStreamer pipeline pumps the camera into a loopback device that appears as an ordinary V4L2 webcam.

This is what Chrome expects without turning on Pipewire support.

Because the bridge holds the sensor open while it runs, it must be started **on-demand** when you need the webcam,

### Manual bridge

Create a loopback device and feed it:

```bash
sudo modprobe v4l2loopback devices=1 video_nr=42 card_label="IPU6 Camera" exclusive_caps=1

gst-launch-1.0 -e icamerasrc ! \
  "video/x-raw(memory:DMABuf),format=DMA_DRM,width=1280,height=720" ! \
  glupload ! glcolorconvert ! gldownload ! "video/x-raw,format=NV12" ! \
  videoconvert ! "video/x-raw,format=YUY2" ! \
  v4l2sink device=/dev/video42
```

`exclusive_caps=1` is required for most apps (Chrome, Firefox, Zoom) to list the node as a capture device. `YUY2` is the format most apps expect. Point any app at **"IPU6 Camera"** (`/dev/video42`); verify with:

```bash
gst-launch-1.0 v4l2src device=/dev/video42 ! videoconvert ! autovideosink
```


## Notes

- `icamerasrc` is a native GStreamer source and does **not** create a `/dev/videoN` V4L2 node. Apps expecting a plain webcam (browsers, conferencing apps, `v4l2src`) will not see it directly; bridge it through `v4l2loopback` if needed.
- The warning `CamHAL[WAR] Failed to open file /run/camera/ov02c10-uf_VIDEO.aiqd` is harmless. `.aiqd` is the AIQ auto-tuning cache the HAL loads at startup and writes at stream stop; on the first run after boot it does not exist yet. Capture proceeds using the shipped `.aiqb` tuning.
