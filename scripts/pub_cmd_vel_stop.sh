#!/usr/bin/env bash
set -eo pipefail

source /opt/ros/humble/setup.bash
source /home/shenfq/Projects/carbot-ros2/install/setup.bash

ros2 topic pub --once --wait-matching-subscriptions 0 /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.0}, angular: {z: 0.0}}"
