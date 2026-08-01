"""
Module Cấu Hình Hệ Thống Định Vị Trong Nhà (IPS)
Chứa toàn bộ các hằng số, tham số cấu hình cho thuật toán và kết nối.
"""

import os
from dotenv import load_dotenv

# Tải các biến môi trường từ file .env (nếu có)
load_dotenv()

# ==============================================================================
# 1. CẤU HÌNH TỌA ĐỘ BEACON CỐ ĐỊNH (Đơn vị: Mét)
# ==============================================================================
# Tọa độ 2D (x, y) của 3 Beacon BLE cố định trong không gian thử nghiệm
BEACON_POSITIONS = {
    "b1": (0.0 , 0.6),    # Beacon 1: Gốc tọa độ (0, 0)
    "b2": (0.0, 0.0),    # Beacon 2: Góc phải dưới (5m, 0m)
    "b3": (1.2, 0.0),    # Beacon 3: Đỉnh tam giác (2.5m, 4m)
}

# ==============================================================================
# 2. CẤU HÌNH MÔ HÌNH TRUYỀN SÓNG RSSI (Log-Distance Path Loss Model)
# ==============================================================================
# Measured Power (A): Giá trị RSSI đo được ở khoảng cách chuẩn 1 mét (dBm)
# Thường nằm trong khoảng -55 dBm đến -65 dBm tùy thiết bị BLE
MEASURED_POWER = float(os.getenv("MEASURED_POWER", "-55.0"))
PATH_LOSS_EXPONENT = float(os.getenv("PATH_LOSS_EXPONENT", "2.5"))

# Giới hạn khoảng cách tối đa và tối thiểu để tránh dị điểm do nhiễu tín hiệu
MIN_DISTANCE_METERS = 0.0
MAX_DISTANCE_METERS = 5.0

# Giá trị RSSI tối thiểu coi như mất tín hiệu
MIN_RSSI_THRESHOLD = -95.0


# ==============================================================================
# 4. CẤU HÌNH MQTT BROKER VÀ BEACON MAC
# ==============================================================================
# Ánh xạ địa chỉ MAC của 3 Beacon thu từ ESP32 Gateway sang tên Beacon
BEACON_MACS = {
    "3c:8a:1f:d4:a0:dc": "b1",
    "e0:72:a1:d7:18:f5": "b2",
    "14:63:93:8c:fa:6e": "b3",
}

MQTT_BROKER = os.getenv("MQTT_BROKER", "192.168.100.234")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPICS = ["beacon/#", "beacon/rssi", "beacon/distance", "beacon/location", "ble/gateway/data"]
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "beacon/#")
MQTT_CLIENT_ID = os.getenv("MQTT_CLIENT_ID", "Python_IPS_Server")
MQTT_KEEPALIVE = 60

# ==============================================================================
# 5. CẤU HÌNH ĐỒ HỌA REALTIME & TỐI ƯU MƯỢT MÀ (Visualizer & Interpolation)
# ==============================================================================
# Thời gian cập nhật đồ thị (Milli-giây) -> 30ms tương đương ~33 FPS
PLOT_UPDATE_INTERVAL_MS = 30

# Hệ số làm mượt nội suy nội suy vị trí (Linear Interpolation Alpha: 0.1 - 0.5)
# Giúp di chuyển Target liên tục mượt mà 33 FPS không bị giật ngay cả khi MQTT gửi thưa
SMOOTH_ALPHA = 0.35

# Số điểm lịch sử lưu vết đường đi của Target
TRAJECTORY_MAX_POINTS = 60

# Giới hạn khung hình hiển thị 2D [xmin, xmax, ymin, ymax] (mét)
MAP_LIMITS = {
    "x_min": -2.0,
    "x_max": 2.0,
    "y_min": -2.0,
    "y_max": 2.0,
}
