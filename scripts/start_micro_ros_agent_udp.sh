#!/usr/bin/env bash
set -eo pipefail

PORT="${1:-8888}"
VERBOSE="${MICRO_ROS_AGENT_VERBOSE:-6}"

source /opt/ros/humble/setup.bash
source /home/shenfq/Projects/micro_ros_agent_ws/install/setup.bash

echo "Starting micro-ROS Agent on UDP port ${PORT}"
echo "Host does not set agent_ip. Configure the ESP32 device's agent_ip to this host's LAN IP, for example: 192.168.1.109"
exec ros2 run micro_ros_agent micro_ros_agent udp4 --port "${PORT}" --verbose "${VERBOSE}"
