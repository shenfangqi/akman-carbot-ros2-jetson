# micro-ROS 上位机配置

当前上位机已安装：

- ROS 2 Humble：`/opt/ros/humble`
- micro-ROS Agent 工作空间：`~/Projects/micro_ros_agent_ws`
- carbot ROS 2 工作空间：`~/Projects/carbot-ros2`

## 当前网络信息

当前 Wi-Fi 接口：

```text
wlP1p1s0
```

当前上位机局域网 IPv4：

```text
192.168.1.109
```

注意：`agent_ip` 不是在上位机设置的。上位机只启动 micro-ROS Agent 并监听 UDP 端口。

ESP32 设备端需要配置 Agent 所在机器的信息：

- `agent_ip = 192.168.1.109`，也就是这台 Ubuntu / Jetson 上位机的局域网 IP
- `agent_port = 8888`，也就是上位机 Agent 监听的 UDP 端口
- Jetson / Ubuntu 上位机和 ESP32 必须在同一个局域网

## 启动 UDP Agent

默认端口 `8888`：

```bash
cd ~/Projects/carbot-ros2
./scripts/start_micro_ros_agent_udp.sh
```

指定端口：

```bash
./scripts/start_micro_ros_agent_udp.sh 8888
```

等 ESP32 启动并连上 Wi-Fi 后，Agent 终端应看到 client/session 相关日志。

## 发布 /cmd_vel 测试

另开一个终端。

前进一次：

```bash
cd ~/Projects/carbot-ros2
./scripts/pub_cmd_vel_once.sh 0.40 0.0
```

持续前进，10 Hz：

```bash
./scripts/pub_cmd_vel_stream.sh 0.40 0.0 10
```

左转：

```bash
./scripts/pub_cmd_vel_stream.sh 0.10 0.8 10
```

右转：

```bash
./scripts/pub_cmd_vel_stream.sh 0.10 -0.8 10
```

停车并回正：

```bash
./scripts/pub_cmd_vel_stop.sh
```

## GUI 控制

另开一个有图形桌面的终端，启动 GUI：

```bash
cd ~/Projects/carbot-ros2
./scripts/start_cmd_vel_gui.sh
```

GUI 会发布 `/cmd_vel`：

- 按住 `Forward`：持续发布前进速度
- 按住 `Backward`：持续发布后退速度
- 按住 `Left`：持续发布左转角速度
- 按住 `Right`：持续发布右转角速度
- 松开方向按钮：发布 stop
- 点击 `STOP`：立即发布 stop

默认参数：

```text
linear_speed = 0.40 m/s
angular_speed = 0.8 rad/s
publish_rate_hz = 10
```

也可以用 ROS 参数覆盖：

```bash
ros2 run carbot_control cmd_vel_gui --ros-args \
  -p linear_speed:=0.10 \
  -p angular_speed:=0.6 \
  -p publish_rate_hz:=10.0
```

## 手写命令版本

启动 Agent：

```bash
source /opt/ros/humble/setup.bash
source ~/Projects/micro_ros_agent_ws/install/setup.bash
ros2 run micro_ros_agent micro_ros_agent udp4 --port 8888 --verbose 6
```

发布速度：

```bash
source /opt/ros/humble/setup.bash
ros2 topic pub --rate 10 /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.40}, angular: {z: 0.0}}"
```

停车：

```bash
ros2 topic pub --once --wait-matching-subscriptions 0 /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.0}, angular: {z: 0.0}}"
```

## 检查 ROS 图

```bash
ros2 node list
ros2 topic list
ros2 topic info /cmd_vel
```

当前 ESP32 第一阶段只订阅 `/cmd_vel`，没有 `/odom`、TF、IMU publisher 或 service。

## ROS_DOMAIN_ID

当前建议先不设置 `ROS_DOMAIN_ID`，保持默认值。micro-ROS Agent 和 ROS 2 CLI 在同一台上位机上运行时，默认配置最简单。

如果以后显式设置 domain id，要确保启动 Agent 的终端和发布 `/cmd_vel` 的终端一致：

```bash
export ROS_DOMAIN_ID=10
```

## 排错

如果 ESP32 没有反应：

1. 确认 ESP32 和上位机在同一 Wi-Fi / 局域网。
2. 确认 ESP32 设备端固件配置里的 `agent_ip` 是上位机 IP：`192.168.1.109`。
3. 确认 ESP32 设备端固件配置里的 `agent_port` 和上位机 Agent 启动端口一致。
4. 先启动 Agent，再重启 ESP32。
5. 看 Agent 终端是否出现 micro-ROS client 连接日志。
6. 用低速测试，例如 `linear.x = 0.10`、`angular.z = 0.0`。
