#!/usr/bin/env bash
set -eo pipefail

LINEAR="${1:-0.40}"
ANGULAR="${2:-0.0}"

source /opt/ros/humble/setup.bash
source /home/shenfq/Projects/carbot-ros2/install/setup.bash

ros2 topic pub --once --wait-matching-subscriptions 0 /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: ${LINEAR}}, angular: {z: ${ANGULAR}}}"
