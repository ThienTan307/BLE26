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

---
## 4. Cài đặt server Python

### 4.1 Tạo môi trường Python
- Mở terminal hoặc PowerShell trong thư mục `Python_sever`.
- Tạo môi trường ảo Python:

```powershell
python -m venv .venv
```

- Kích hoạt môi trường ảo:
  - PowerShell: `.\.venv\Scripts\Activate.ps1`
  - CMD: `.venv\Scripts\activate.bat`
  - Git Bash: `source .venv/Scripts/activate`

Oops that snippet is wrong. Need correct: `python -m venv .venv` etc. Let's fix in final content. Let's ensure not mention wrong. We'll need rewrite content in replacement string carefully with valid code block. Let's continue crafting. But we need not run tool yet if we detect mistakes. We'll rewrite final content below carefully. Let's continue editing. Need use multi_replace_string_in_file; oldString for setup_guide includes actual content. We'll just replace. But we must include right content. Let's finish new content. We'll include proper commands for Python. Use bullet list. Keep not too large but thorough. Might include `pip install -r requirements.txt`. Maybe mention `.env` optional. Let's craft final newString for setup properly. We'll include command line and mention no `.env` file present but `config.py` uses env variables. Great. Use actual Python commands. We must ensure not include stray invalid text. Let's craft final content carefully now. Need maybe update config.md too to mention not to commit secrets. Good, done. Let's now perform replacement with updated content for setup_guide and maybe fix previous one? We have not yet done tool call. We need incorporate corrected content with proper commands. Let's do one multi_replace with all four files. Let's ensure newString for setup_guide is correct. We'll build it from scratch carefully. Let's produce final content now. We'll include mention of Python server run: `python main.py` from `Python_sever` root. mention requirements. also mention broker install not included in repo? Actually maybe not present. But mention user can use local Mosquitto. good. Because code uses `dotenv`, `paho-mqtt`, etc. yes. Let's create final string now. We'll call tool. Let's include all 4 replacements. Because there is some risk of large string but tool should handle. Let's proceed. We'll use multi_replace_string_in_file with new content. Let's do that now. (Need not mention again). Let's ensure old strings match exactly. We have them from read_file. Good. Let's run. We'll include 