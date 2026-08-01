"""
Mô-đun Quản Lý Kết Nối MQTT (MQTT Client Handler)
Khởi tạo Paho-MQTT Client, kết nối Broker, lắng nghe tin nhắn từ Gateway ESP32:
- Topic 'beacon/rssi': Dữ liệu RSSI từng Beacon theo MAC address
- Topic 'beacon/distance': Dữ liệu khoảng cách d1, d2, d3 do ESP32 tính sẵn
- Topic 'beacon/location': Tọa độ x, y do ESP32 tính sẵn
- Topic 'ble/gateway/data': Dữ liệu RSSI tổng hợp 3 Beacon
"""

import json
import logging
import threading
import paho.mqtt.client as mqtt

from config import (
    MQTT_BROKER,
    MQTT_PORT,
    MQTT_TOPICS,
    MQTT_CLIENT_ID,
    MQTT_KEEPALIVE,
    BEACON_MACS,
)
from core.positioning import PositionEngine

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


class MQTTManager:
    """
    Lớp quản lý kết nối MQTT Client, nhận dữ liệu đã được ESP32 Gateway tính toán sẵn
    và cập nhật kết quả trực tiếp lên Python Server Visualizer.
    """

    def __init__(self, position_engine: PositionEngine = None):
        self.engine = position_engine or PositionEngine()
        self.client = mqtt.Client(client_id=MQTT_CLIENT_ID, clean_session=True)

        self._lock = threading.Lock()

        # Giá trị RSSI hiện tại của 3 Beacon
        self.current_rssi = {
            "b1": -70.0,
            "b2": -70.0,
            "b3": -70.0,
        }

        # Dữ liệu vị trí mới nhất lưu giữ để visualizer đọc hiển thị
        self.latest_result = {
            "raw_rssi": (-70.0, -70.0, -70.0),
            "distances": (0.0, 0.0, 0.0),
            "position": (0.0, 0.0),
        }

        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect

    def _on_connect(self, client, userdata, flags, rc):
        """Callback khi kết nối thành công đến MQTT Broker."""
        if rc == 0:
            logging.info(f"Đã kết nối thành công đến MQTT Broker: {MQTT_BROKER}:{MQTT_PORT}")
            for topic in MQTT_TOPICS:
                client.subscribe(topic)
                logging.info(f"Đã subscribe topic: '{topic}'")
        else:
            logging.error(f"Kết nối MQTT thất bại với mã lỗi rc={rc}")

    def _on_disconnect(self, client, userdata, rc):
        """Callback khi mất kết nối MQTT Broker."""
        logging.warning(f"Mất kết nối MQTT Broker (rc={rc}). Đang kết nối lại...")

    def _on_message(self, client, userdata, msg):
        """
        Callback khi nhận tin nhắn từ ESP32 Gateway.
        Nhận dữ liệu tính toán sẵn từ ESP32 đẩy qua MQTT, không tính toán lại ở Python.
        """
        try:
            topic = msg.topic
            payload_str = msg.payload.decode("utf-8").strip()
            logging.debug(f"MQTT Received [{topic}]: {payload_str}")

            # ------------------------------------------------------------------
            # 1. Xử lý Topic 'beacon/rssi' (Gửi từng Beacon theo MAC address)
            # ------------------------------------------------------------------
            if topic == "beacon/rssi":
                data = json.loads(payload_str)
                mac = data.get("address", "").lower()
                rssi_val = float(data.get("rssi", -99))

                beacon_key = BEACON_MACS.get(mac)
                if not beacon_key:
                    for k, m in BEACON_MACS.items():
                        if k.lower() == mac:
                            beacon_key = m
                            break

                if beacon_key:
                    self.current_rssi[beacon_key] = rssi_val
                    with self._lock:
                        self.latest_result["raw_rssi"] = (
                            self.current_rssi["b1"],
                            self.current_rssi["b2"],
                            self.current_rssi["b3"],
                        )

            # ------------------------------------------------------------------
            # 2. Xử lý Topic 'beacon/distance' (Khoảng cách d1, d2, d3 từ ESP32)
            # ------------------------------------------------------------------
            elif topic == "beacon/distance":
                data = json.loads(payload_str)
                d1 = float(data.get("d1", 0.0))
                d2 = float(data.get("d2", 0.0))
                d3 = float(data.get("d3", 0.0))

                with self._lock:
                    self.latest_result["distances"] = (d1, d2, d3)

            # ------------------------------------------------------------------
            # 3. Xử lý Topic 'beacon/location' (Tọa độ x, y do Gateway ESP32 tính sẵn)
            # ------------------------------------------------------------------
            elif topic == "beacon/location":
                data = json.loads(payload_str)
                x = float(data.get("x", 0.0))
                y = float(data.get("y", 0.0))

                with self._lock:
                    self.latest_result["position"] = (x, y)

            # ------------------------------------------------------------------
            # 4. Xử lý Topic tổng hợp 'ble/gateway/data' hoặc các dạng JSON khác
            # ------------------------------------------------------------------
            else:
                rssi1, rssi2, rssi3 = None, None, None
                if payload_str.startswith("{") and payload_str.endswith("}"):
                    data = json.loads(payload_str)
                    rssi1 = float(data.get("rssi1", data.get("b1", -70)))
                    rssi2 = float(data.get("rssi2", data.get("b2", -70)))
                    rssi3 = float(data.get("rssi3", data.get("b3", -70)))
                elif "|" in payload_str or "," in payload_str:
                    sep = "|" if "|" in payload_str else ","
                    parts = [float(p.strip()) for p in payload_str.split(sep)]
                    if len(parts) >= 3:
                        rssi1, rssi2, rssi3 = parts[0], parts[1], parts[2]

                if rssi1 is not None and rssi2 is not None and rssi3 is not None:
                    self.current_rssi["b1"] = rssi1
                    self.current_rssi["b2"] = rssi2
                    self.current_rssi["b3"] = rssi3
                    with self._lock:
                        self.latest_result["raw_rssi"] = (rssi1, rssi2, rssi3)

        except Exception as e:
            logging.error(f"Lỗi khi xử lý tin nhắn MQTT trên topic '{msg.topic}': {e}")

    def start(self):
        """Kết nối và khởi chạy MQTT Loop trên background thread."""
        try:
            self.client.connect(MQTT_BROKER, MQTT_PORT, MQTT_KEEPALIVE)
            self.client.loop_start()
            logging.info(f"MQTT Client đang lắng nghe trên Broker {MQTT_BROKER}:{MQTT_PORT}...")
        except Exception as e:
            logging.error(f"Không thể kết nối đến MQTT Broker {MQTT_BROKER}:{MQTT_PORT}: {e}")

    def stop(self):
        """Dừng MQTT Client."""
        self.client.loop_stop()
        self.client.disconnect()
        logging.info("Đã dừng MQTT Client.")

    def get_latest_data(self) -> dict:
        """Đọc dữ liệu mới nhất nhận từ ESP32 (Thread-safe)."""
        with self._lock:
            return self.latest_result.copy()
