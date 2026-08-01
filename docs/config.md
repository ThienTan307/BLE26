# Cấu Hình Hệ Thống

Tài liệu này trình bày tất cả cấu hình quan trọng của hệ thống, bao gồm kết nối WiFi, MQTT, MAC Beacon, tham số RSSI và thông số hiển thị của server Python.

---
## 1. Cấu hình WiFi và MQTT cho Gateway ESP32

File: `Filmware_gateway/src/main_gateway.cpp`

### WiFi
```cpp
const char* ssid = "THIEN TAN";
const char* password = "0912345678";
```

- `ssid`: tên mạng WiFi cần kết nối.
- `password`: mật khẩu mạng.

> ESP32 hoạt động ổn định nhất với WiFi 2.4GHz. Nếu dùng mạng 5GHz, thiết bị có thể không bắt được.

### MQTT Broker
```cpp
const char* mqtt_server = "192.168.100.234";
const int mqtt_port = 1883;
```

- `mqtt_server`: IP của MQTT Broker.
- `mqtt_port`: cổng kết nối MQTT (thường là `1883`).

### Topics MQTT quan trọng
| Topic | Nội dung |
|---|---|
| `beacon/rssi` | RSSI thô từng beacon dưới dạng JSON object. |
| `beacon/distance` | Khoảng cách d1/d2/d3 do ESP32 tính. |
| `beacon/location` | Tọa độ 2D `x`, `y` do ESP32 tính. |

---
## 2. Cấu hình Beacon và tọa độ

File: `Filmware_gateway/src/main_gateway.cpp`

```cpp
BeaconConfig myBeaconConfigs[3] = {
    {"3c:8a:1f:d4:a0:dc", 0.0 , 0.6 , -60, 3.5}, 
    {"e0:72:a1:d7:18:f5", 0.0 , 0.0 , -60, 3.5},
    {"14:63:93:8c:fa:6e", 1.2 , 0.0, -60, 3.5}
};
```

#### Ý nghĩa các trường
- `macAddress`: địa chỉ MAC của beacon.
- `x`, `y`: tọa độ vật lý cố định của beacon (mét).
- `A`: RSSI đo được ở khoảng cách 1 mét.
- `n`: hệ số suy hao môi trường.

### Ví dụ cấu hình beacon hiện tại
| Beacon | MAC Address | X (m) | Y (m) | A | n |
|---|---|---|---|---|---|
| B1 | `3c:8a:1f:d4:a0:dc` | `0.0` | `0.6` | `-60` | `3.5` |
| B2 | `e0:72:a1:d7:18:f5` | `0.0` | `0.0` | `-60` | `3.5` |
| B3 | `14:63:93:8c:fa:6e` | `1.2` | `0.0` | `-60` | `3.5` |

> Nếu bạn thay đổi vị trí vật lý của beacon, cần cập nhật lại các giá trị `x`, `y` tương ứng.

---
## 3. Tham số mô hình RSSI

File: `Filmware_gateway/src/localization.cpp`

- `A` và `n` quyết định cách RSSI được chuyển sang khoảng cách.
- Nếu RSSI không hợp lệ (>= 0 hoặc <= -95), hàm `rssiToDistance` trả về `-1.0`.
- Khoảng cách trả về được giới hạn trong `0.05m` đến `10.0m`.

### Gợi ý hiệu chỉnh
- Nếu giá trị vị trí dao động nhiều: thử điều chỉnh `A` và `n` theo môi trường thực tế.
- Môi trường nhiều vật cản, gương, kim loại ảnh hưởng lớn đến RSSI.

---
## 4. Cấu hình server Python

File: `Python_sever/config.py`

### MQTT Broker
```python
MQTT_BROKER = os.getenv("MQTT_BROKER", "192.168.100.234")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_CLIENT_ID = os.getenv("MQTT_CLIENT_ID", "Python_IPS_Server")
MQTT_TOPICS = ["beacon/#", "beacon/rssi", "beacon/distance", "beacon/location", "ble/gateway/data"]
```

- `MQTT_BROKER`: địa chỉ broker.
- `MQTT_PORT`: cổng broker.
- `MQTT_CLIENT_ID`: tên client.
- `MQTT_TOPICS`: các topic server sẽ subscribe.

### Ánh xạ MAC beacon
```python
BEACON_MACS = {
    "3c:8a:1f:d4:a0:dc": "b1",
    "e0:72:a1:d7:18:f5": "b2",
    "14:63:93:8c:fa:6e": "b3",
}
```

- Dùng để ánh xạ MAC beacon thành tên nội bộ `b1`, `b2`, `b3`.
- Nếu thay MAC trong firmware Gateway, cập nhật ở đây.

### Vị trí beacon trên bản đồ
```python
BEACON_POSITIONS = {
    "b1": (0.0 , 0.6),
    "b2": (0.0, 0.0),
    "b3": (1.2, 0.0),
}
```

- `BEACON_POSITIONS` dùng để hiển thị vị trí cố định của các beacon.
- Nếu bố trí vật lý thay đổi, chỉnh lại các tọa độ.

### Cấu hình đồ họa
```python
MAP_LIMITS = {
    "x_min": -2.0,
    "x_max": 2.0,
    "y_min": -2.0,
    "y_max": 2.0,
}
PLOT_UPDATE_INTERVAL_MS = 30
SMOOTH_ALPHA = 0.35
TRAJECTORY_MAX_POINTS = 60
```

- `MAP_LIMITS`: giới hạn hiển thị.
- `PLOT_UPDATE_INTERVAL_MS`: tần suất cập nhật biểu đồ (ms).
- `SMOOTH_ALPHA`: độ mượt khi nội suy vị trí.
- `TRAJECTORY_MAX_POINTS`: số điểm lịch sử quỹ đạo.

---
## 5. Lưu ý khi công khai repository
- Không commit mật khẩu WiFi thật vào repo công khai.
- Nên dùng biến môi trường hoặc ghi chú người dùng tự cấu hình.
- Các MAC beacon và tham số môi trường nên để ở dạng ví dụ, không phải thông tin riêng tư.
