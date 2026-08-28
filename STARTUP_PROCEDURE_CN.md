# Carbot 项目启动流程

本文总结 `carbot-ros2` 项目的常用启动步骤。当前项目由 ROS 2 Humble、micro-ROS Agent、`carbot_control` 控制包和 ESP32 设备端组成。

## 1. 前提条件

当前机器应已安装并准备好：

- ROS 2 Humble：`/opt/ros/humble`
- micro-ROS Agent 工作空间：`~/Projects/micro_ros_agent_ws`
- Carbot ROS 2 工作空间：`~/Projects/carbot-ros2`

ESP32 设备端需要和上位机在同一个局域网，并配置：

- `agent_ip`：上位机的局域网 IP，例如 `192.168.1.109`
- `agent_port`：默认 `8888`

注意：`agent_ip` 是 ESP32 设备端配置，不是在上位机启动脚本里设置。上位机只负责监听 UDP 端口。

启动顺序很重要：必须先启动 ROS 上位机侧的 micro-ROS Agent，再启动或重启 ESP32 设备端。否则设备端可能无法建立 micro-ROS 会话，需要重启设备端重新连接。

## 2. 构建 ROS 2 工作空间

第一次运行、修改代码后、或者 `install/` 目录不存在时，需要重新构建：

```bash
cd ~/Projects/carbot-ros2
source /opt/ros/humble/setup.bash
colcon build --packages-select carbot_control
source install/setup.bash
```

如果要构建整个工作空间：

```bash
colcon build
source install/setup.bash
```

## 3. 启动 micro-ROS Agent

打开第一个终端，启动 UDP Agent：

```bash
cd ~/Projects/carbot-ros2
./scripts/start_micro_ros_agent_udp.sh
```

默认端口是 `8888`。如果需要指定端口：

```bash
./scripts/start_micro_ros_agent_udp.sh 8888
```

启动后，保持这个终端运行。ESP32 上电并连上 Wi-Fi 后，Agent 终端应该能看到 client/session 相关日志。

## 4. 启动 ESP32 设备端

确认 micro-ROS Agent 已经在上位机运行后，再启动或重启 ESP32。不要先启动 ESP32 再启动上位机 Agent；如果顺序反了，建议保持 Agent 运行，然后重启 ESP32。

ESP32 设备端当前主要订阅 `/cmd_vel`，用于接收车体运动速度命令。当前第一阶段没有 `/odom`、TF、IMU publisher 或 service。

## 5. 用脚本测试速度命令

打开第二个终端，进入项目目录。

前进一次，线速度 `0.40 m/s`：

```bash
cd ~/Projects/carbot-ros2
./scripts/pub_cmd_vel_once.sh 0.40 0.0
```

持续前进，10 Hz 发布：

```bash
./scripts/pub_cmd_vel_stream.sh 0.40 0.0 10
```

左转测试：

```bash
./scripts/pub_cmd_vel_stream.sh 0.10 0.8 10
```

右转测试：

```bash
./scripts/pub_cmd_vel_stream.sh 0.10 -0.8 10
```

停车并回正：

```bash
./scripts/pub_cmd_vel_stop.sh
```

## 6. 启动 GUI 控制

如果上位机有图形桌面，可以用 GUI 控制 `/cmd_vel`。

打开新的图形终端：

```bash
cd ~/Projects/carbot-ros2
./scripts/start_cmd_vel_gui.sh
```

GUI 默认参数：

```text
linear_speed = 0.40 m/s
angular_speed = 0.8 rad/s
publish_rate_hz = 10
```

GUI 操作方式：

- 按住 `Forward`：持续前进
- 按住 `Backward`：持续后退
- 按住 `Left`：持续左转
- 按住 `Right`：持续右转
- 松开方向按钮：发布停车命令
- 点击 `STOP`：立即发布停车命令

也可以直接用 ROS 参数覆盖 GUI 默认速度：

```bash
source /opt/ros/humble/setup.bash
source ~/Projects/carbot-ros2/install/setup.bash
ros2 run carbot_control cmd_vel_gui --ros-args \
  -p linear_speed:=0.10 \
  -p angular_speed:=0.6 \
  -p publish_rate_hz:=10.0
```

## 7. 启动 carbot_driver 节点

如果需要运行项目里的 `carbot_driver` launch 文件：

```bash
cd ~/Projects/carbot-ros2
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch carbot_control carbot.launch.py
```

该节点会按参数周期性发布 `/cmd_vel`。当前 launch 默认：

```text
linear_speed = 0.40 m/s
angular_speed = 0.0 rad/s
publish_period = 0.2 s
```

运行中也可以修改参数：

```bash
ros2 param set /carbot_driver linear_speed 0.4
```

## 8. 检查 ROS 图和 Topic

常用检查命令：

```bash
ros2 node list
ros2 topic list
ros2 topic info /cmd_vel
ros2 topic echo /cmd_vel
```

检查 `carbot_driver` 参数：

```bash
ros2 param list
ros2 param get /carbot_driver linear_speed
```

## 9. 手写命令版本

如果不使用脚本，可以手动启动 Agent：

```bash
source /opt/ros/humble/setup.bash
source ~/Projects/micro_ros_agent_ws/install/setup.bash
ros2 run micro_ros_agent micro_ros_agent udp4 --port 8888 --verbose 6
```

手动发布持续前进命令：

```bash
source /opt/ros/humble/setup.bash
ros2 topic pub --rate 10 /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.40}, angular: {z: 0.0}}"
```

手动停车：

```bash
ros2 topic pub --once --wait-matching-subscriptions 0 /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.0}, angular: {z: 0.0}}"
```

## 10. 推荐启动顺序

日常测试推荐顺序：

1. 上位机连接到和 ESP32 相同的 Wi-Fi / 局域网。
2. 确认 ESP32 固件里的 `agent_ip` 是当前上位机 IP。
3. 在上位机启动 `./scripts/start_micro_ros_agent_udp.sh`。
4. Agent 正常运行后，再启动或重启 ESP32，等待 Agent 终端出现连接日志。
5. 用 `./scripts/pub_cmd_vel_once.sh 0.40 0.0` 做一次前进测试。
6. 用 `./scripts/pub_cmd_vel_stop.sh` 停车。
7. 需要人工连续控制时，启动 `./scripts/start_cmd_vel_gui.sh`。

## 11. 常见问题排查

如果 ESP32 没有反应：

1. 确认 ESP32 和上位机在同一局域网。
2. 确认 ESP32 设备端的 `agent_ip` 是上位机当前局域网 IP。
3. 确认 ESP32 设备端的 `agent_port` 和 Agent 启动端口一致，默认是 `8888`。
4. 必须先启动 micro-ROS Agent，再启动或重启 ESP32；如果 ESP32 已经先启动，保持 Agent 运行并重启 ESP32。
5. 查看 Agent 终端是否有 client/session 日志。
6. 用低速命令测试，例如 `linear.x = 0.10`、`angular.z = 0.0`。
7. 检查 `/cmd_vel` 是否正在发布：`ros2 topic echo /cmd_vel`。

## 12. 停车命令

测试结束后，建议显式发送停车命令：

```bash
cd ~/Projects/carbot-ros2
./scripts/pub_cmd_vel_stop.sh
```
