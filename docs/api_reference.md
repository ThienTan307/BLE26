# API Reference và Mô tả các Module Chính

Tài liệu này giải thích các chức năng quan trọng trong dự án, giúp người mới biết cách từng phần của firmware ESP32 và server Python hoạt động.

---
## 1. Beacon BLE tĩnh (Filmware_beacon)

### File chính
- `Filmware_beacon/src/main_beacon.cpp`
- `Filmware_beacon/include/beacon.h`

### `BLEBeacon`

`BLEBeacon` là lớp đơn giản để khởi tạo và phát quảng bá BLE.

#### Constructor
- `BLEBeacon(String name)`
  - Nhận tên beacon và lưu vào thuộc tính `beaconName`.

#### Phương thức
- `void begin()`
  - Gọi `BLEDevice::init(beaconName.c_str())` để khởi động BLE.
  - Tạo `BLEServer` và lấy `BLEAdvertising`.
  - Cấu hình `setScanResponse(true)` và `setMinPreferred(0x06)`.
  - Bắt đầu phát quảng bá BLE bằng `pAdvertising->start()`.
  - In log `Beacon đang phát sóng...`.

### Hành vi chương trình
- `setup()` khởi tạo Serial và gọi `myBeacon.begin()`.
- `loop()` chỉ chứa `delay(1000)` để giữ chương trình hoạt động.

Beacon không quét BLE, chỉ phát tín hiệu để Gateway thu thập.

---
## 2. Gateway BLE và MQTT (Filmware_gateway)

Firmware Gateway chịu trách nhiệm:
- Quét các gói quảng bá BLE.
- Lọc theo MAC address của Beacon mục tiêu.
- Lưu RSSI và lọc bằng EMA.
- Tính khoảng cách từ RSSI.
- Tính tọa độ 2D bằng phương pháp trilateration.
- Publish dữ liệu lên MQTT Broker.

### 2.1 `BLEGateway` (`gateway.h`, `gateway.cpp`)

#### Thuộc tính chính
- `String beaconMacs[3]`
  - Danh sách 3 địa chỉ MAC Beacon cần theo dõi.
- `int rawRssiValues[3]`
  - RSSI thô nhận được cuối cùng cho mỗi Beacon.
- `float filteredRssiValues[3]`
  - RSSI sau lọc EMA.
- `unsigned long lastSeenTimes[3]`
  - Thời điểm beacon được quét thấy lần cuối.
- `BLEScan* pBLEScan`
  - Con trỏ bộ quét BLE.

#### `BLEGateway()`
- Gán 3 MAC cố định.
- Khởi tạo RSSI mặc định `-100`.
- Khởi tạo thời gian `lastSeenTimes` bằng `millis()`.

#### `void begin()`
- Khởi tạo BLE bằng `BLEDevice::init("Gateway")`.
- Lấy đối tượng quét bằng `BLEDevice::getScan()`.
- Tạo callback `GatewayCallbacks(this)` để xử lý kết quả quét.
- Bật `setActiveScan(true)`.
- Cấu hình thời gian quét bằng `setInterval(160)` và `setWindow(120)`.

#### `void scanAndPrint()`
- Bắt đầu quét 1 giây bằng `pBLEScan->start(1, false)`.
- Nếu beacon không được quét trong 6 giây, reset RSSI về `-100`.
- In ra Serial log trạng thái RSSI đã lọc.
- Xóa kết quả quét cũ với `pBLEScan->clearResults()`.

#### `void updateRSSI(String mac, int rssi)`
- So sánh MAC quét được với danh sách beacon mục tiêu.
- `matchMacAddress()` hỗ trợ so sánh không phân biệt chữ hoa/chữ thường và kiểm tra cả prefix/suffix.
- Nếu trùng match:
  - Cập nhật `rawRssiValues[i]` và `lastSeenTimes[i]`.
  - Cập nhật `filteredRssiValues[i]` bằng EMA:
    `filteredRssiValues[i] = 0.4f*rssi + 0.6f*filteredRssiValues[i]`.
- Nếu thiết bị khác có MAC trông giống ESP32, in log debug.

#### `int* getRssiValues()`
- Trả về mảng 3 giá trị RSSI đã lọc.

#### `int getFilteredRssi(int index)`
- Trả RSSI đã lọc theo chỉ số 0..2.

### 2.2 `GatewayCallbacks`

- `GatewayCallbacks(BLEGateway* instance)` lưu tham chiếu đến `BLEGateway`.
- `void onResult(BLEAdvertisedDevice device)` lấy MAC và RSSI rồi gọi `updateRSSI()`.

---
## 3. Định vị và chuyển đổi RSSI

### 3.1 `BeaconConfig` (`localization.h`)

```cpp
struct BeaconConfig {
    String macAddress;
    double x;
    double y;
    double A;
    double n;
};
```

- `macAddress`: MAC của beacon.
- `x`, `y`: tọa độ cố định theo mét.
- `A`: RSSI tại 1m.
- `n`: hệ số suy hao môi trường.

### 3.2 `rssiToDistance(int rssi, double A, double n)`

- Chuyển RSSI thành khoảng cách bằng mô hình Log-Distance Path Loss.
- Nếu RSSI >= 0 hoặc <= -95, trả về `-1.0` để báo lỗi.
- Giới hạn trong khoảng `0.05m` đến `10.0m`.

### 3.3 `calculateGatewayPosition(double d1, double d2, double d3, BeaconConfig beacons[])`

- Dùng phương pháp tối ưu gradient descent để tìm tọa độ phù hợp nhất với 3 khoảng cách.
- Bắt đầu từ tâm tam giác tạo bởi 3 beacon.
- Lặp 100 bước, cập nhật `x` và `y` theo đạo hàm của sai số.
- Trả về `Point` với `x` và `y`.
- Nếu không thể tính được (định thức xấp xỉ 0), trả về `{-1.0, -1.0}`.

### 3.4 `EMAFilter` (`ema_filter.cpp`)

- `EMAFilter(double a)`: khởi tạo hệ số alpha.
- `double update(double raw_value)`: nếu chưa khởi tạo thì gán giá trị đầu tiên, ngược lại áp dụng công thức EMA.
- `void reset()`: đặt lại trạng thái lọc.

---
## 4. Server Python (Python_sever)

### 4.1 `MQTTManager` (`Python_sever/core/mqtt_client.py`)

- Kết nối đến broker MQTT và subscribe các topic quan trọng.
- Cập nhật dữ liệu nhận được từ `beacon/rssi`, `beacon/distance`, `beacon/location`.
- Lưu trạng thái mới nhất vào `self.latest_result`.
- Cung cấp `get_latest_data()` để visualizer đọc dữ liệu thread-safe.

### 4.2 `PositionEngine` (`Python_sever/core/positioning.py`)

- Cung cấp hàm `calculate_beacon_distances(target_x, target_y)`.
- Dùng cấu hình beacon từ `config.py` để tính khoảng cách hình học.
- `get_geometric_distances(x, y)` trả về bộ khoảng cách từ vị trí đến 3 beacon.

### 4.3 `PositionVisualizer` (`Python_sever/core/visualizer.py`)

- Vẽ đồ thị 2D thời gian thực bằng Matplotlib.
- Hiển thị các beacon cố định, các vòng tròn bán kính khoảng cách và vị trí Gateway.
- Nội suy bằng LERP để làm mượt chuyển động.
- Cập nhật thông số RSSI, khoảng cách và tọa độ trên bảng text.

---
## 5. MQTT Topic và Định dạng dữ liệu

| Topic | Định dạng | Nội dung | Mô tả |
|---|---|---|---|
| `beacon/rssi` | JSON object | `{"address":"<mac>","rssi":-65}` | RSSI thô từng beacon, gửi từng bản tin một. |
| `beacon/distance` | JSON object | `{"d1":1.23,"d2":2.34,"d3":3.45}` | Khoảng cách tính từ RSSI trên Gateway ESP32. |
| `beacon/location` | JSON object | `{"x":1.23,"y":0.56}` | Tọa độ 2D của Gateway do ESP32 tính. |
| `ble/gateway/data` | JSON object or string | `{"b1":-65,"b2":-70,"b3":-72}` | Dạng payload bổ sung nếu cần dữ liệu tổng hợp. |

---
## 6. Hợp nhất giữa firmware và server

1. `main_gateway.cpp` quét BLE, lấy RSSI và tính khoảng cách.
2. `rssiToDistance()` chuyển RSSI thành d1/d2/d3.
3. `calculateGatewayPosition()` tính `(x, y)` từ 3 khoảng cách.
4. `sendMQTTArray()`, `sendDistanceMQTT()`, `sendPositionMQTT()` publish dữ liệu.
5. `MQTTManager` nhận và lưu dữ liệu.
6. `PositionVisualizer` vẽ vị trí và cập nhật thời gian thực.

> Đây là tài liệu tham khảo cho người muốn mở rộng hoặc sửa lỗi dự án.
