# Hướng Dẫn Thiết Lập và Chạy Dự Án

Tài liệu này hướng dẫn bạn từng bước để cài đặt, biên dịch và chạy toàn bộ hệ thống từ Beacon BLE, Gateway ESP32 đến server Python.

---
## 1. Yêu cầu cơ bản

### 1.1 Phần cứng
- 3 x board ESP32 làm Beacon BLE.
- 1 x board ESP32-S3 làm Gateway.
- 1 x máy tính cài đặt MQTT Broker và Python.
- Cáp USB phù hợp cho từng board.
- Mạng WiFi 2.4GHz chung cho Gateway và máy tính.

### 1.2 Phần mềm
- Visual Studio Code + plugin PlatformIO.
- Python 3.10+ (hoặc 3.11+).
- Các thư viện Python trong `Python_sever/requirements.txt`.
- MQTT Broker (ví dụ Mosquitto).

---
## 2. Cài đặt và flash Beacon

Beacon chỉ phát quảng bá BLE, không cần cấu hình phức tạp.

### 2.1 Mở dự án Beacon
- Mở thư mục `Filmware_beacon` trong VS Code.
- Kiểm tra file `platformio.ini` để chọn môi trường phù hợp với board.

### 2.2 Biên dịch và nạp chương trình
- Mở `Filmware_beacon/src/main_beacon.cpp`.
- Chọn board phù hợp ở thanh dưới hoặc trong `platformio.ini`.
- Nhấn `Build` để biên dịch.
- Kết nối board Beacon với máy tính qua USB.
- Nhấn `Upload` để ghi firmware.

### 2.3 Kiểm tra địa chỉ MAC
- Mở Serial Monitor (115200 baud).
- Khởi động reboot board và đọc dòng hiển thị `BLE MAC Address cua thiet bi nay:`.
- Ghi lại địa chỉ MAC của từng beacon.
- Lặp lại cho 3 board Beacon.

> Mỗi beacon cần có MAC khác nhau và bạn phải dùng đúng MAC này trong cấu hình Gateway.

---
## 3. Cài đặt và flash Gateway

Gateway quét BLE, tính toán vị trí và gửi MQTT.

### 3.1 Mở dự án Gateway
- Mở thư mục `Filmware_gateway` trong VS Code.

### 3.2 Cấu hình WiFi và MQTT
Mở file `Filmware_gateway/src/main_gateway.cpp` và chỉnh lại:

```cpp
const char* ssid = "<TEN_MANG_WIFI>";
const char* password = "<MAT_KHAU_WIFI>";
const char* mqtt_server = "<DIA_CHI_BROKER>";
const int mqtt_port = 1883;
```

- `ssid`: tên mạng WiFi 2.4GHz.
- `password`: mật khẩu WiFi.
- `mqtt_server`: IP của máy tính chạy broker.
- `mqtt_port`: cổng broker, mặc định `1883`.

### 3.3 Cập nhật MAC Beacon
- Trong `main_gateway.cpp`, cập nhật đúng 3 MAC đã lấy từ bước Beacon:

```cpp
BeaconConfig myBeaconConfigs[3] = {
    {"<MAC_BEACON_1>", 0.0 , 0.6 , -60, 3.5},
    {"<MAC_BEACON_2>", 0.0 , 0.0 , -60, 3.5},
    {"<MAC_BEACON_3>", 1.2 , 0.0, -60, 3.5}
};
```

- Trong `Filmware_gateway/src/gateway.cpp`, hàm khởi tạo `BLEGateway()` cũng chứa 3 MAC mặc định. Bạn nên đồng bộ Mac ở cả hai chỗ nếu cần.

### 3.4 Biên dịch và nạp Gateway
- Biên dịch dự án `Filmware_gateway`.
- Kết nối board ESP32-S3 với máy tính.
- Nạp chương trình vào board.
- Mở Serial Monitor (115200 baud) để quan sát log.

