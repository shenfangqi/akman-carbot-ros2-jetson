from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription(
        [
            Node(
                package="carbot_control",
                executable="carbot_driver",
                name="carbot_driver",
                output="screen",
                parameters=[
                    {
                        "linear_speed": 0.40,
                        "angular_speed": 0.0,
                        "publish_period": 0.2,
                    }
                ],
            )
        ]
    )
