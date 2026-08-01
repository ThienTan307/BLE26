"""
Mô-đun Quản Lý Tọa Độ và Khoảng Cách Hình Học (Core Positioning Helper)
Bao gồm các hàm hỗ trợ tính toán khoảng cách hình học từ Gateway đến 3 Beacon cố định.
Toàn bộ thuật toán tính toán vị trí (Trilateration) và lọc RSSI được thực hiện trên ESP32 Gateway.
"""

import math
from config import BEACON_POSITIONS


def calculate_beacon_distances(target_x: float, target_y: float, beacon_positions: dict = None) -> tuple:
    """
    Tính khoảng cách hình học R_i từ 3 Beacon đến vị trí Gateway (target_x, target_y).
    Đảm bảo 3 vòng tròn có bán kính R_1, R_2, R_3 luôn cắt nhau chính xác tại điểm Gateway.
    
    :param target_x: Tọa độ X của Gateway
    :param target_y: Tọa độ Y của Gateway
    :param beacon_positions: Từ điển vị trí các Beacon
    :return: Tuple (r1, r2, r3) bán kính 3 vòng tròn (mét)
    """
    beacons = beacon_positions or BEACON_POSITIONS
    b1_x, b1_y = beacons["b1"]
    b2_x, b2_y = beacons["b2"]
    b3_x, b3_y = beacons["b3"]

    r1 = math.sqrt((target_x - b1_x) ** 2 + (target_y - b1_y) ** 2)
    r2 = math.sqrt((target_x - b2_x) ** 2 + (target_y - b2_y) ** 2)
    r3 = math.sqrt((target_x - b3_x) ** 2 + (target_y - b3_y) ** 2)

    return r1, r2, r3


class PositionEngine:
    """
    Lớp lưu trữ thông tin cấu hình và khoảng cách hình học.
    """

    def __init__(self, beacon_positions: dict = None):
        self.beacons = beacon_positions or BEACON_POSITIONS
        self.b1_pos = self.beacons["b1"]
        self.b2_pos = self.beacons["b2"]
        self.b3_pos = self.beacons["b3"]

    def get_geometric_distances(self, x: float, y: float) -> tuple:
        """Trả về khoảng cách từ vị trí (x, y) đến 3 beacon."""
        return calculate_beacon_distances(x, y, self.beacons)
