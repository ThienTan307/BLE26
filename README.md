# BLE-IPS
BLE_indoor positioning system applying IOT tech 
## 📌 Project Overview

**BLE-IPS** is an IoT-integrated **Indoor Positioning System** that utilizes **Bluetooth Low Energy (BLE)**, **Exponential Moving Average (EMA)** noise filtering, and **Trilateration** algorithms to determine the real-time 2D location of a mobile unit within an indoor environment[cite: 1, 3].

The system hardware setup consists of:
* **3 Static Beacons (ESP32):** Three fixed ESP32 microcontrollers continuously broadcast BLE advertisement signals to act as physical reference anchors[cite: 1, 3, 4].
* **1 Mobile Gateway (ESP32-S3):** An ESP32-S3 unit that scans BLE signals from the 3 beacons, filters raw RSSI values using an **EMA algorithm** to eliminate signal noise, converts signal strength to distance using the Log-Distance Path Loss model, and computes its own 2D $(x, y)$ coordinates via **trilateration**[cite: 1, 3, 4].

The processed location and distance data are transmitted over Wi-Fi via **MQTT** to a Python-based server for real-time 2D mapping and visualization[cite: 1, 3].

---

### 🏗️ System Architecture

1. **`Filmware_beacon` (ESP32):** Firmware for the 3 stationary BLE beacons[cite: 3].
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
