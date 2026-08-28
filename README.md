# carbot-ros2

A humble ROS 2 starter workspace for a small car robot.

This project uses a Python ROS 2 package because Python is the simpler default
for early robot behavior, launch files, sensors, and control experiments. If the
robot later needs high-rate control loops or heavier compute, add C++ packages
alongside this one.

## Layout

```text
carbot-ros2/
  src/
    carbot_control/
      carbot_control/
      launch/
      config/
```

## Build

From this directory, after ROS 2 Humble is installed and sourced:

```bash
source /opt/ros/humble/setup.bash
colcon build
source install/setup.bash
```

## Run

```bash
ros2 launch carbot_control carbot.launch.py
```

The starter node publishes a gentle forward velocity on `/cmd_vel` and logs
incoming `/odom` messages.
