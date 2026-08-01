# Tổng Quan Kiến Trúc Dự Án (Indoor Positioning System - IPS)

Dự án này xây dựng một hệ thống định vị trong nhà dựa trên **Bluetooth Low Energy (BLE)** và **định vị ba cạnh (trilateration)**. Mục tiêu là xác định vị trí 2D của một thiết bị Gateway di động dựa trên tín hiệu thu được từ ba thiết bị Beacon cố định.

---
## 1. Ý nghĩa và mục tiêu

- **Thu thập tín hiệu BLE** từ các thiết bị Beacon cố định.
- **Ước lượng khoảng cách** giữa Gateway và từng Beacon bằng RSSI (Received Signal Strength Indicator).
- **Tính toán vị trí Gateway** trên mặt phẳng 2D bằng phương pháp Trilateration.
- **Đưa dữ liệu lên MQTT Broker** để xử lý, vận hành và trực quan hóa thời gian thực.

Đây là một dự án học tập phù hợp cho người mới muốn tìm hiểu IoT, ESP32, BLE, MQTT và thuật toán định vị trong nhà.

---
## 2. Cấu trúc thư mục chính

Dự án được tổ chức thành 3 phần mã nguồn chính và thư mục tài liệu `docs`:

- `Filmware_beacon`: firmware ESP32 cho các Beacon BLE tĩnh.
- `Filmware_gateway`: firmware ESP32 cho Gateway quét BLE, tính toán vị trí và gửi dữ liệu qua MQTT.
- `Python_sever`: ứng dụng Python chạy trên máy tính, nhận MQTT và hiển thị vị trí bằng đồ họa.
- `docs`: chứa tài liệu `overview.md`, `api_reference.md`, `config.md`, `setup_guide.md`.

---
## 3. Thành phần chính của hệ thống

### 3.1 Beacon BLE tĩnh

- Mỗi thiết bị trong `Filmware_beacon` là một ESP32 phát quảng bá BLE liên tục.
- Beacon chỉ có nhiệm vụ phát sóng BLE để Gateway có thể quét và lấy RSSI.
- Mã nguồn chính: `Filmware_beacon/src/main_beacon.cpp`.

### 3.2 Gateway ESP32

- Gateway quét BLE, nhận RSSI từ 3 Beacon có MAC cố định.
- Tính toán khoảng cách từ RSSI bằng mô hình Log-Distance Path Loss.
- Tính tọa độ 2D bằng Trilateration.
- Gửi dữ liệu RSSI và vị trí lên MQTT Broker qua WiFi.
- Mã nguồn chính: `Filmware_gateway/src/main_gateway.cpp`, `Filmware_gateway/src/gateway.cpp`, `Filmware_gateway/src/localization.cpp`, `Filmware_gateway/src/ema_filter.cpp`.

### 3.3 Python Server

- Nhận dữ liệu MQTT từ Gateway.
- Lưu giữ RSSI, khoảng cách và tọa độ mới nhất.
- Vẽ trực quan vị trí Gateway trên đồ thị Matplotlib.
- Mã nguồn chính: `Python_sever/main.py`, `Python_sever/core/mqtt_client.py`, `Python_sever/core/positioning.py`, `Python_sever/core/visualizer.py`.

---
## 4. Luồng dữ liệu tổng thể

1. **Beacon BLE** phát quảng bá BLE.
2. **Gateway ESP32** quét BLE, lọc theo MAC Beacon, thu RSSI.
3. **Gateway** chuyển RSSI sang khoảng cách và giải thuật định vị.
4. **Gateway** gửi dữ liệu lên **MQTT Broker**.
5. **Python Server** nhận dữ liệu, hiển thị đồ thị và cập nhật vị trí.

---
## 5. Workflow chi tiết

### 5.1 Beacon

- Khởi động và gọi `BLEDevice::init()` để bắt đầu BLE.
- Không có vòng `loop()` xử lý nhiều; beacon chỉ phát quảng bá liên tục.

### 5.2 Gateway

- `BLEGateway::begin()` khởi tạo BLE và cấu hình quét.
- `GatewayCallbacks::onResult()` nhận kết quả quét BLE và gọi `BLEGateway::updateRSSI()`.
- `BLEGateway::scanAndPrint()` quét 1 giây và cập nhật giá trị RSSI đã lọc.
- `main_gateway.cpp` xử lý WiFi/MQTT, chuyển RSSI sang khoảng cách, tính vị trí và gửi MQTT.

### 5.3 Python Server

- `MQTTManager` kết nối đến broker, đăng ký các topic `beacon/#`.
- Khi nhận payload MQTT, nó cập nhật cấu trúc dữ liệu nội bộ và trả về cho `PositionVisualizer`.
- `PositionVisualizer` vẽ lại biểu đồ mỗi 30ms, hiển thị vị trí Gateway và vòng tròn khoảng cách đến 3 beacon.

---
## 6. Tài liệu này dành cho ai?

- Người mới tiếp cận công nghệ **ESP32 / BLE / MQTT**.
- Người muốn học cách xây dựng hệ thống định vị trong nhà đơn giản.
- Người cần tham khảo cấu trúc dự án, mô tả các file chính và ý nghĩa của thuật toán.

> Lưu ý: Các cấu hình MAC, WiFi và tham số tín hiệu cần điều chỉnh theo môi trường thực tế khi triển khai.
