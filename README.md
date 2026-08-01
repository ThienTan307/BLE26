# BLE-IPS
BLE_indoor positioning system applying IOT tech 
## 📌 Project Overview

**BLE-IPS** is an IoT-integrated **Indoor Positioning System** that utilizes **Bluetooth Low Energy (BLE)**, **Exponential Moving Average (EMA)** noise filtering, and **Trilateration** algorithms to determine the real-time 2D location of a mobile unit within an indoor environment[cite: 1, 3].

The system hardware setup consists of:
* **3 Static Beacons (ESP32-C3):** Three fixed ESP32 microcontrollers continuously broadcast BLE advertisement signals to act as physical reference anchors[cite: 1, 3, 4].
* **1 Mobile Gateway (ESP32-S3):** An ESP32-S3 unit that scans BLE signals from the 3 beacons, filters raw RSSI values using an **EMA algorithm** to eliminate signal noise, converts signal strength to distance using the Log-Distance Path Loss model, and computes its own 2D $(x, y)$ coordinates via **trilateration**[cite: 1, 3, 4].

The processed location and distance data are transmitted over Wi-Fi via **MQTT** to a Python-based server for real-time 2D mapping and visualization[cite: 1, 3].

---

### 🏗️ System Architecture

1. **`Filmware_beacon` (ESP32-C3):** Firmware for the 3 stationary BLE beacons[cite: 3].
2. **`Filmware_gateway` (ESP32-S3):** Firmware for the mobile gateway handling BLE scanning, EMA filtering, trilateration math, and MQTT publication[cite: 1, 3].
3. **`Python_sever`:** Python backend that consumes MQTT telemetry and renders the gateway's real-time trajectory using Matplotlib[cite: 1, 3].

---

### 🔄 Data Workflow

```text
[ 3x ESP32 Beacons ] ──(BLE Signals)──> [ ESP32-S3 Gateway ] ──(MQTT / Wi-Fi)──> [ Python Server ] ──> [ 2D Visualizer ]
                                        └─ EMA Filtering 
                                        └─ Trilateration
```
```text
  ┌─────────────────┐
  │ 3x ESP32 Nodes  │ ─── (BLE Signal Broadcast) ───┐
  └─────────────────┘                               │
                                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    ESP32-S3 Mobile Gateway                              │
│                                                                         │
│  [ BLE Scan ] ──> [ EMA RSSI Filter ] ──> [ Log-Distance Path Loss ]     │
│                                                   │                     │
│                                                   ▼                     │
│                                       [ 2D Trilateration Math ]         │
└─────────────────────────────────────────────────────────────────────────┘
                                                    │
                                             (Wi-Fi / MQTT)
                                                    │
                                                    ▼
                             ┌────────────────────────────────────────┐
                             │    Python Server & 2D Visualizer      │
                             └────────────────────────────────────────┘
```
---

```
PIC 1: Dynamic position tracking test — Evaluating the system response and tracking performance as the ESP32-S3 Gateway changes location in real time.
```
<img width="2232" height="2564" alt="image" src="https://github.com/user-attachments/assets/4acd0490-134e-4b0b-befa-095d16261f7d" />
---
```
Real-time terminal log displaying raw vs. EMA-filtered RSSI values alongside calculated distances ($d_1, d_2, d_3$) and 2D coordinates ($X, Y$).
```
<img width="1916" height="1018" alt="image" src="https://github.com/user-attachments/assets/4f646b59-eb42-4cd5-b015-673265547b3e" />

<img width="1917" height="1078" alt="image" src="https://github.com/user-attachments/assets/976617d7-7833-41f9-93d1-1cef3e56908d" />

---
```

```

