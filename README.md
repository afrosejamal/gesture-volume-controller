# 🖐️ Gesture-Based Volume Controller

Control your system's volume in real time using just your hand and a webcam — no mouse, no keyboard. Built with **OpenCV** and **MediaPipe** for hand tracking, and **Pycaw** to control Windows system audio directly.

🎥 **[Watch the demo](demo/demo.mp4)**

---

## 📌 Overview

This project tracks your hand via webcam, measures the distance between your **thumb tip** and **index fingertip**, and maps that distance to the system volume — pinch fingers together for silence, spread them apart for max volume. A live on-screen bar and FPS counter give instant visual feedback.

---

## 🎯 Key Features

- **Real-time hand tracking** using MediaPipe's 21-point hand landmark model
- **Direct system volume control** via the Windows Core Audio API (Pycaw)
- **Exponential smoothing** on the volume signal to prevent jittery, unstable volume jumps
- **Live visual feedback** — on-screen volume bar, percentage readout, and FPS counter
- **Single-hand detection** tuned for responsiveness (`min_detection_confidence=0.7`)

---

## 🛠️ Tech Stack

| Library | Purpose |
|---|---|
| OpenCV | Webcam capture & on-screen drawing |
| MediaPipe | Hand landmark detection |
| Pycaw | Windows system audio control |
| comtypes | COM interface binding (required by Pycaw) |

---

## 🚀 How to Run

**Requirements:** Windows OS (Pycaw is Windows-only), Python 3.8+, a webcam

```bash
# 1. Clone the repo
git clone https://github.com/afrosejamal/gesture-volume-controller.git
cd gesture-volume-controller

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run it
python volume_controller.py
```

Press **ESC** to quit.

---

## ⚙️ How It Works

1. MediaPipe detects 21 hand landmarks per frame from the webcam feed
2. The Euclidean distance between landmark `4` (thumb tip) and landmark `8` (index tip) is calculated
3. This distance is linearly mapped from a `MIN_DIST`–`MAX_DIST` pixel range to a `0.0`–`1.0` volume scalar
4. An exponential smoothing filter (`alpha = 0.7`) stabilizes the signal frame-to-frame
5. `pycaw` sets the actual system master volume via `SetMasterVolumeLevelScalar`

---

## ⚠️ Limitations

- Windows-only (Pycaw depends on the Windows Core Audio API)
- Single-hand tracking only
- Accuracy depends on lighting and webcam quality

## 🔮 Future Improvements

- [ ] Cross-platform audio support (e.g. `pyaudio` or OS-agnostic alternative for Mac/Linux)
- [ ] Multi-gesture support (mute, play/pause) using additional landmark combinations
- [ ] On-screen calibration step for different hand sizes/distances from camera

---

## 👤 Author

**Afrose Jamal**
📧 afrosepvt@gmail.com
🔗 [LinkedIn](http://www.linkedin.com/in/afrose-fathima-jamal-492b57291)

⭐ *Star this repo if you found it useful!*
