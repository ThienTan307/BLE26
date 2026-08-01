"""
Entrypoint Chính Của Ứng Dụng (Indoor Positioning System Server)
Khởi chạy kết nối MQTT Manager và Giao diện 2D Realtime Visualizer.
Dữ liệu khoảng cách và vị trí được ESP32 Gateway tính toán và truyền qua MQTT.
"""

import sys
import logging
from core.positioning import PositionEngine
from core.mqtt_client import MQTTManager
from core.visualizer import PositionVisualizer

# Cấu hình log đầu ra chuẩn
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger("IPS_Main")


def main():
    """Hàm khởi chạy chính của hệ thống IPS."""
    logger.info("==================================================")
    logger.info("  KHỞI CHẠY HỆ THỐNG ĐỊNH VỊ TRONG NHÀ (BLE IPS)  ")
    logger.info("==================================================")


    logger.info("Khởi tạo mô-đun quản lý không gian 2D...")
    position_engine = PositionEngine()

    logger.info("Khởi tạo MQTT Client Handler...")
    mqtt_manager = MQTTManager(position_engine=position_engine)


    logger.info("Bắt đầu kết nối MQTT Broker...")
    mqtt_manager.start()


    logger.info("Khởi tạo cửa sổ đồ họa 2D Visualizer...")
    visualizer = PositionVisualizer(data_provider_callback=mqtt_manager.get_latest_data)

    try:
        logger.info("Ứng dụng đang chạy. Đóng cửa sổ đồ thị hoặc nhấn CTRL+C để thoát.")
        visualizer.start()
    except KeyboardInterrupt:
        logger.info("\nNhận tín hiệu dừng từ người dùng (CTRL+C).")
    except Exception as e:
        logger.error(f"Lỗi không mong muốn: {e}")
    finally:
      
        logger.info("Đang dọn dẹp tài nguyên và ngắt kết nối MQTT...")
        mqtt_manager.stop()
        logger.info("Đã thoát ứng dụng an toàn.")
        sys.exit(0)


if __name__ == "__main__":
    main()
