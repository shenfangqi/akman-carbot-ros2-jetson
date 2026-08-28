#!/usr/bin/env bash
set -eo pipefail

source /opt/ros/humble/setup.bash
source /home/shenfq/Projects/carbot-ros2/install/setup.bash

exec ros2 run carbot_control cmd_vel_gui
