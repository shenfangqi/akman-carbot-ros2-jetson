# micro-ROS Agent 上位机配置过程

这份文档记录了在当前 Ubuntu / Jetson 上位机上配置 micro-ROS Agent 的原因和实际步骤。

## 为什么需要 `micro_ros_agent_ws`

ESP32 端运行的是 micro-ROS client。它不能直接和普通 ROS 2 graph 完整通信，需要一个运行在上位机上的 micro-ROS Agent 作为桥接进程。

通信关系是：

```text
ESP32 micro-ROS client  <-- UDP -->  micro-ROS Agent  <-- ROS 2 DDS -->  ROS 2 CLI / nodes
```

当前 ROS 2 Humble 已经通过 apt 安装到了：

```text
/opt/ros/humble
```

但当前 Humble apt 源里没有可直接安装并运行的 `micro_ros_agent` 可执行包。可以通过 apt 找到 `ros-humble-micro-ros-msgs` 等消息包，但没有现成的 Agent binary。

因此需要从源码构建 micro-ROS Agent。为了不把 Agent 的源码、构建产物和 `carbot-ros2` 应用工程混在一起，单独创建了一个 ROS 2 workspace：

```text
~/Projects/micro_ros_agent_ws
```

这样目录职责更清楚：

- `~/Projects/carbot-ros2`：你的 carbot ROS 2 上位机应用、脚本和文档
- `~/Projects/micro_ros_agent_ws`：micro-ROS Agent 工具本身

构建完成后，`carbot-ros2` 里的脚本只需要 source Agent workspace：

```bash
source ~/Projects/micro_ros_agent_ws/install/setup.bash
```

## 当前结果

Agent workspace：

```text
~/Projects/micro_ros_agent_ws
```

Agent package prefix：

```text
~/Projects/micro_ros_agent_ws/install/micro_ros_agent
```

启动脚本：

```text
~/Projects/carbot-ros2/scripts/start_micro_ros_agent_udp.sh
```

当前上位机 Wi-Fi IP：

```text
192.168.1.109
```

默认 Agent UDP port：

```text
8888
```

注意：`agent_ip` 配置在 ESP32 设备端，不配置在上位机。ESP32 端的 `agent_ip` 应该填上位机 IP，例如 `192.168.1.109`。

## 配置步骤记录

1. 确认 ROS 2 Humble 已可用：

   ```bash
   source /opt/ros/humble/setup.bash
   ros2 pkg prefix rclpy
   colcon --help
   ```

2. 检查 apt 源中是否有 micro-ROS Agent：

   ```bash
   apt-cache policy ros-humble-micro-ros-agent ros-humble-micro-ros-msgs
   apt-cache search micro-ros
   ```

   结果：能找到 `ros-humble-micro-ros-msgs`，但没有可直接安装的 `ros-humble-micro-ros-agent` binary。

3. 创建 Agent workspace：

   ```bash
   mkdir -p ~/Projects/micro_ros_agent_ws/src
   ```

4. 克隆 micro-ROS Agent Humble 分支：

   ```bash
   git clone -b humble https://github.com/micro-ROS/micro-ROS-Agent.git \
     ~/Projects/micro_ros_agent_ws/src/micro-ROS-Agent
   ```

5. 安装 Agent 构建依赖：

   ```bash
   sudo apt install -y ros-humble-micro-ros-msgs
   ```

6. 检查 rosdep：

   ```bash
   cd ~/Projects/micro_ros_agent_ws
   source /opt/ros/humble/setup.bash
   rosdep install --from-paths src --ignore-src -r -y
   ```

7. 构建 Agent：

   ```bash
   cd ~/Projects/micro_ros_agent_ws
   source /opt/ros/humble/setup.bash
   colcon build
   ```

   构建过程中 CMake 会下载并编译 eProsima Micro-XRCE-DDS-Agent。当前构建成功。

8. 验证 Agent package：

   ```bash
   source /opt/ros/humble/setup.bash
   source ~/Projects/micro_ros_agent_ws/install/setup.bash
   ros2 pkg prefix micro_ros_agent
   ```

   结果：

   ```text
   /home/shenfq/Projects/micro_ros_agent_ws/install/micro_ros_agent
   ```

9. 将 Agent workspace 加入 `~/.bashrc`：

   ```bash
   # micro-ROS Agent workspace
   if [ -f /home/shenfq/Projects/micro_ros_agent_ws/install/setup.bash ]; then
       source /home/shenfq/Projects/micro_ros_agent_ws/install/setup.bash
   fi
   ```

10. 创建 UDP Agent 启动脚本：

    ```text
    ~/Projects/carbot-ros2/scripts/start_micro_ros_agent_udp.sh
    ```

    脚本核心命令：

    ```bash
    ros2 run micro_ros_agent micro_ros_agent udp4 --port "${PORT}" --verbose "${VERBOSE}"
    ```

11. 短暂启动 Agent 验证：

    ```bash
    timeout 3 ~/Projects/carbot-ros2/scripts/start_micro_ros_agent_udp.sh 8888
    ```

    看到类似输出即说明 UDP Agent 可以启动：

    ```text
    running... | port: 8888
    logger setup | verbose_level: 6
    ```

## 日常使用

启动 UDP Agent：

```bash
cd ~/Projects/carbot-ros2
./scripts/start_micro_ros_agent_udp.sh 8888
```

另开一个终端发布 `/cmd_vel`：

```bash
cd ~/Projects/carbot-ros2
./scripts/pub_cmd_vel_once.sh 0.10 0.0
```

持续发布：

```bash
./scripts/pub_cmd_vel_stream.sh 0.40 0.0 10
```

停车回正：

```bash
./scripts/pub_cmd_vel_stop.sh
```

## ESP32 端需要匹配的配置

ESP32 设备端配置：

```text
agent_ip = 192.168.1.109
agent_port = 8888
```

含义：

- `agent_ip` 是上位机的局域网 IP
- `agent_port` 是上位机 micro-ROS Agent 监听的 UDP 端口
- ESP32 和上位机必须在同一个局域网

## 注意事项

- `192.168.1.109` 是当前 DHCP 分配的地址，之后可能变化。
- 正式跑车前应再次确认上位机 IP。
- 如果 IP 变化，需要修改 ESP32 设备端的 `agent_ip` 配置。
- 上位机不设置 `agent_ip`，只监听 UDP port。
- 当前 ESP32 第一阶段只订阅 `/cmd_vel`，没有 publisher、service、`/odom`、TF 或 IMU 发布。
