import rclpy
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from rclpy.node import Node


class CarbotDriver(Node):
    def __init__(self):
        super().__init__("carbot_driver")

        self.declare_parameter("linear_speed", 0.40)
        self.declare_parameter("angular_speed", 0.0)
        self.declare_parameter("publish_period", 0.2)

        self.cmd_vel_pub = self.create_publisher(Twist, "cmd_vel", 10)
        self.odom_sub = self.create_subscription(
            Odometry,
            "odom",
            self.handle_odom,
            10,
        )

        period = self.get_parameter("publish_period").value
        self.timer = self.create_timer(period, self.publish_drive_command)
        self.get_logger().info("carbot_driver started")

    def publish_drive_command(self):
        msg = Twist()
        msg.linear.x = float(self.get_parameter("linear_speed").value)
        msg.angular.z = float(self.get_parameter("angular_speed").value)
        self.cmd_vel_pub.publish(msg)

    def handle_odom(self, msg):
        position = msg.pose.pose.position
        self.get_logger().debug(
            f"odom position x={position.x:.2f}, y={position.y:.2f}"
        )


def main(args=None):
    rclpy.init(args=args)
    node = CarbotDriver()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
