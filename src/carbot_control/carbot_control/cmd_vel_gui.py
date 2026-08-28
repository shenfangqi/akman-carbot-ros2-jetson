import tkinter as tk

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node


class CmdVelGui(Node):
    def __init__(self):
        super().__init__("carbot_cmd_vel_gui")

        self.declare_parameter("linear_speed", 0.40)
        self.declare_parameter("angular_speed", 0.8)
        self.declare_parameter("publish_rate_hz", 10.0)

        self.publisher = self.create_publisher(Twist, "cmd_vel", 10)
        self.active_linear = 0.0
        self.active_angular = 0.0
        self.publishing = False

        self.root = tk.Tk()
        self.root.title("Carbot")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.close)

        self.status_var = tk.StringVar(value="STOP")
        self._build_ui()
        self._bind_keyboard()

        period_ms = int(1000.0 / float(self.get_parameter("publish_rate_hz").value))
        self.publish_period_ms = max(period_ms, 20)
        self.root.after(self.publish_period_ms, self._tick)

    def _build_ui(self):
        self.root.configure(bg="#f4f6f8", padx=22, pady=20)

        panel = tk.Frame(self.root, bg="#f4f6f8")
        panel.grid(row=0, column=0)

        button_opts = {
            "width": 10,
            "height": 3,
            "font": ("Sans", 12, "bold"),
            "relief": "raised",
            "bd": 2,
            "activebackground": "#dbeafe",
        }

        forward = tk.Button(panel, text="Forward", **button_opts)
        left = tk.Button(panel, text="Left", **button_opts)
        right = tk.Button(panel, text="Right", **button_opts)
        backward = tk.Button(panel, text="Backward", **button_opts)
        stop = tk.Button(
            panel,
            text="STOP",
            width=12,
            height=2,
            font=("Sans", 13, "bold"),
            bg="#ef4444",
            fg="white",
            activebackground="#dc2626",
            activeforeground="white",
        )

        forward.grid(row=0, column=1, padx=8, pady=8)
        left.grid(row=1, column=0, padx=8, pady=8)
        right.grid(row=1, column=2, padx=8, pady=8)
        backward.grid(row=2, column=1, padx=8, pady=8)
        stop.grid(row=3, column=1, padx=8, pady=(18, 8))

        self._wire_motion_button(forward, "FORWARD", 1.0, 0.0)
        self._wire_motion_button(backward, "BACKWARD", -1.0, 0.0)
        self._wire_motion_button(left, "LEFT", 0.0, 1.0)
        self._wire_motion_button(right, "RIGHT", 0.0, -1.0)
        stop.configure(command=self.stop)

        status = tk.Label(
            self.root,
            textvariable=self.status_var,
            font=("Sans", 12),
            bg="#f4f6f8",
            fg="#111827",
            width=22,
        )
        status.grid(row=1, column=0, pady=(12, 0))

    def _bind_keyboard(self):
        bindings = {
            "<KeyPress-Up>": ("FORWARD", 1.0, 0.0),
            "<KeyPress-Down>": ("BACKWARD", -1.0, 0.0),
            "<KeyPress-Left>": ("LEFT", 0.0, 1.0),
            "<KeyPress-Right>": ("RIGHT", 0.0, -1.0),
        }

        for sequence, command in bindings.items():
            self.root.bind(sequence, lambda _event, cmd=command: self.start_motion(*cmd))

        for sequence in (
            "<KeyRelease-Up>",
            "<KeyRelease-Down>",
            "<KeyRelease-Left>",
            "<KeyRelease-Right>",
        ):
            self.root.bind(sequence, lambda _event: self.stop())

        self.root.bind("<space>", lambda _event: self.stop())

    def _wire_motion_button(self, button, label, linear_scale, angular_scale):
        button.bind(
            "<ButtonPress-1>",
            lambda _event: self.start_motion(label, linear_scale, angular_scale),
        )
        button.bind("<ButtonRelease-1>", lambda _event: self.stop())

    def start_motion(self, label, linear_scale, angular_scale):
        linear_speed = float(self.get_parameter("linear_speed").value)
        angular_speed = float(self.get_parameter("angular_speed").value)
        self.active_linear = linear_scale * linear_speed
        self.active_angular = angular_scale * angular_speed
        self.publishing = True
        self.status_var.set(label)
        self.publish_cmd(self.active_linear, self.active_angular)

    def stop(self):
        self.active_linear = 0.0
        self.active_angular = 0.0
        self.publishing = False
        self.status_var.set("STOP")
        self.publish_cmd(0.0, 0.0)

    def publish_cmd(self, linear, angular):
        msg = Twist()
        msg.linear.x = float(linear)
        msg.angular.z = float(angular)
        self.publisher.publish(msg)

    def _tick(self):
        rclpy.spin_once(self, timeout_sec=0.0)

        if self.publishing:
            self.publish_cmd(self.active_linear, self.active_angular)

        self.root.after(self.publish_period_ms, self._tick)

    def close(self):
        self.stop()
        self.root.destroy()

    def run(self):
        self.root.mainloop()


def main(args=None):
    rclpy.init(args=args)
    gui = CmdVelGui()

    try:
        gui.run()
    finally:
        gui.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
