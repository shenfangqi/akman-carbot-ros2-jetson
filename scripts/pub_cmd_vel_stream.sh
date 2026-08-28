#!/usr/bin/env bash
set -eo pipefail

LINEAR="${1:-0.40}"
ANGULAR="${2:-0.0}"
RATE="${3:-10}"

source /opt/ros/humble/setup.bash
source /home/shenfq/Projects/carbot-ros2/install/setup.bash

ros2 topic pub --rate "${RATE}" /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: ${LINEAR}}, angular: {z: ${ANGULAR}}}"
