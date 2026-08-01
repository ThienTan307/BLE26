"""
Mô-đun Trực Quan Hóa Không Gian 2D Realtime (2D Position Visualizer)
Sử dụng Matplotlib và Matplotlib Animation kết hợp nội suy LERP (Linear Interpolation) 33 FPS:
1. 3 Beacon BLE cố định với bán kính 3 vòng tròn tự động cắt nhau chính xác tại Gateway.
2. Vị trí điểm Gateway (x, y) thời gian thực di chuyển siêu mượt mà.
3. Vết lịch sử quỹ đạo di chuyển (Trajectory tail).
4. Khung thông số chi tiết (RSSI, Khoảng cách đo lường từ ESP32, Khoảng cách hình học đến Gateway).
"""

import math
from collections import deque
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation

from config import (
    BEACON_POSITIONS,
    MAP_LIMITS,
    PLOT_UPDATE_INTERVAL_MS,
    SMOOTH_ALPHA,
    TRAJECTORY_MAX_POINTS,
)


class PositionVisualizer:
    """
    Lớp tạo giao diện đồ họa 2D hiển thị hệ thống định vị thời gian thực.
    Tối ưu nội suy vị trí LERP giúp chuyển động siêu mượt ở 33 FPS.
    """

    def __init__(self, data_provider_callback, beacon_positions: dict = None):
        """
        :param data_provider_callback: Hàm callback trả về thông tin dữ liệu mới nhất (dict) từ MQTTManager
        :param beacon_positions: Tọa độ 3 beacon cố định
        """
        self.get_data = data_provider_callback
        self.beacons = beacon_positions or BEACON_POSITIONS

        # Lưu vết lịch sử di chuyển
        self.trajectory_x = deque(maxlen=TRAJECTORY_MAX_POINTS)
        self.trajectory_y = deque(maxlen=TRAJECTORY_MAX_POINTS)

        # Biến tọa độ hiển thị được nội suy LERP (Render LERP Variables)
        self.render_x = None
        self.render_y = None

        # Cấu hình Figure và Subplot của Matplotlib
        plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
        self.fig, self.ax = plt.subplots(figsize=(9, 8))
        self.fig.canvas.manager.set_window_title("Indoor Positioning System (IPS) - 2D Realtime Tracker")

        # Khởi tạo các thành phần đồ họa (Artists)
        self._init_artists()

    def _init_artists(self):
        """Khởi tạo các thành phần vẽ cố định và động trên đồ thị."""
        # 1. Cấu hình giới hạn và tiêu đề khung đồ thị 2D
        self.ax.set_xlim(MAP_LIMITS["x_min"], MAP_LIMITS["x_max"])
        self.ax.set_ylim(MAP_LIMITS["y_min"], MAP_LIMITS["y_max"])
        self.ax.set_xlabel("Trục X (Mét)", fontsize=11, fontweight="bold")
        self.ax.set_ylabel("Trục Y (Mét)", fontsize=11, fontweight="bold")
        self.ax.set_title("HỆ THỐNG ĐỊNH VỊ TRONG NHÀ (BLE IPS - REALTIME TRACKER)", fontsize=13, fontweight="bold", pad=12)
        self.ax.set_aspect("equal", adjustable="box")
        self.ax.grid(True, linestyle="--", alpha=0.6)

        # 2. Vẽ 3 Beacon cố định và khởi tạo 3 vòng tròn bán kính
        colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]
        self.circles = {}
        for idx, (b_name, b_pos) in enumerate(self.beacons.items()):
            color = colors[idx % len(colors)]
            # Điểm Beacon
            self.ax.scatter(
                b_pos[0], b_pos[1],
                color=color, marker="s", s=140, edgecolors="black", linewidth=1.5,
                zorder=5, label=f"Beacon {b_name.upper()} ({b_pos[0]:.1f}m, {b_pos[1]:.1f}m)"
            )
            # Nhãn tên Beacon
            self.ax.text(
                b_pos[0], b_pos[1] + 0.15, f"{b_name.upper()}",
                fontsize=10, fontweight="bold", ha="center", color=color
            )
            # Khởi tạo 3 đường tròn bán kính khoảng cách (Circle Patches)
            circle = patches.Circle(
                (b_pos[0], b_pos[1]), radius=0.1,
                fill=False, color=color, linestyle="--", linewidth=1.5, alpha=0.7, zorder=3
            )
            self.ax.add_patch(circle)
            self.circles[b_name] = circle

        # 3. Thành phần vẽ lịch sử quỹ đạo di chuyển (Line2D)
        (self.line_trajectory,) = self.ax.plot(
            [], [], color="#d62728", linestyle=":", linewidth=2, alpha=0.7, zorder=4, label="Lịch sử quỹ đạo"
        )

        # 4. Thành phần vẽ vị trí Gateway hiện tại
        self.target_scatter = self.ax.scatter(
            [], [], color="#d62728", marker="o", s=180, edgecolors="white", linewidth=2.0,
            zorder=6, label="Vị trí Gateway (x, y)"
        )

        # 5. Khung chữ hiển thị thông số hệ thống (Overlay Text Box)
        self.info_text = self.ax.text(
            0.02, 0.96, "", transform=self.ax.transAxes,
            fontsize=9.5, verticalalignment="top",
            bbox=dict(boxstyle="round,pad=0.5", facecolor="white", edgecolor="#cccccc", alpha=0.9)
        )

        self.ax.legend(loc="upper right", frameon=True, facecolor="white", framealpha=0.9, fontsize=9)

    def _update_plot(self, frame):
        """Hàm cập nhật đồ thị sau mỗi 30ms kết hợp nội suy LERP làm mượt chuyển động."""
        data = self.get_data()

        d_meas = data.get("distances", (0.0, 0.0, 0.0))
        target_x, target_y = data.get("position", (0.0, 0.0))
        raw_rssi = data.get("raw_rssi", (-70.0, -70.0, -70.0))

        # Khởi tạo hoặc nội suy LERP làm mượt vị trí Gateway
        if self.render_x is None:
            self.render_x = target_x
            self.render_y = target_y
        else:
            self.render_x += (target_x - self.render_x) * SMOOTH_ALPHA
            self.render_y += (target_y - self.render_y) * SMOOTH_ALPHA

        # Tính toán bán kính 3 vòng tròn sao cho cả 3 đường tròn CẮT NGANG qua con Gateway
        b1_x, b1_y = self.beacons["b1"]
        b2_x, b2_y = self.beacons["b2"]
        b3_x, b3_y = self.beacons["b3"]

        r1 = math.sqrt((self.render_x - b1_x) ** 2 + (self.render_y - b1_y) ** 2)
        r2 = math.sqrt((self.render_x - b2_x) ** 2 + (self.render_y - b2_y) ** 2)
        r3 = math.sqrt((self.render_x - b3_x) ** 2 + (self.render_y - b3_y) ** 2)

        # Cập nhật bán kính 3 đường tròn
        self.circles["b1"].set_radius(r1)
        self.circles["b2"].set_radius(r2)
        self.circles["b3"].set_radius(r3)

        # Cập nhật điểm vị trí Gateway
        self.target_scatter.set_offsets([[self.render_x, self.render_y]])

        # Cập nhật đường lịch sử quỹ đạo
        self.trajectory_x.append(self.render_x)
        self.trajectory_y.append(self.render_y)
        self.line_trajectory.set_data(self.trajectory_x, self.trajectory_y)

        # Cập nhật nội dung bảng thông số text
        text_str = (
            f"📍 TỌA ĐỘ GATEWAY REALTIME:\n"
            f"   X = {self.render_x:5.2f} m | Y = {self.render_y:5.2f} m\n\n"
            f"📡 THÔNG SỐ BEACON (TỪ ESP32 & HÌNH HỌC):\n"
            f"   • B1: RSSI={raw_rssi[0]:.0f}dBm | d_esp32={d_meas[0]:.2f}m | r_map={r1:.2f}m\n"
            f"   • B2: RSSI={raw_rssi[1]:.0f}dBm | d_esp32={d_meas[1]:.2f}m | r_map={r2:.2f}m\n"
            f"   • B3: RSSI={raw_rssi[2]:.0f}dBm | d_esp32={d_meas[2]:.2f}m | r_map={r3:.2f}m"
        )
        self.info_text.set_text(text_str)

        return list(self.circles.values()) + [self.target_scatter, self.line_trajectory, self.info_text]

    def start(self):
        """Bắt đầu vòng lặp hoạt họa Matplotlib (FuncAnimation)."""
        anim = FuncAnimation(
            self.fig,
            self._update_plot,
            interval=PLOT_UPDATE_INTERVAL_MS,
            blit=False
        )
        plt.tight_layout()
        plt.show()
