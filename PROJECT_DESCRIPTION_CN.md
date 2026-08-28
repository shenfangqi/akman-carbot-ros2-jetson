# AKMan Carbot ROS 2 Jetson 项目详细说明

## 1. 项目简介

`akman-carbot-ros2-jetson` 是一个面向小型轮式机器人的 ROS 2 控制项目。系统以 Jetson 或 Ubuntu 主机作为上位机，以 ESP32 作为底层控制器，通过 ROS 2 Humble、micro-ROS Agent 和局域网 UDP 通信建立完整的运动控制链路。

项目当前阶段的主要目标是打通以下基础链路：

```text
ROS 2 控制节点 / 图形遥控器
              |
              | geometry_msgs/msg/Twist
              | Topic: /cmd_vel
              v
       ROS 2 DDS 通信图
              |
              v
   micro-ROS Agent（UDP 8888）
              |
              v
        ESP32 micro-ROS Client
              |
              v
          电机驱动与小车
```

上位机统一通过标准 `/cmd_vel` Topic 输出运动命令。ESP32 只需要订阅该 Topic 并驱动电机，无需了解命令来自 GUI、测试脚本、自动控制节点还是未来的导航系统。这种设计让控制来源和底层执行相互解耦，也为后续接入 Nav2、视觉感知和自主导航保留了标准接口。

## 2. 当前功能

项目已经实现以下上位机功能：

- ROS 2 Humble Python 控制包 `carbot_control`。
- 周期性速度指令发布节点 `carbot_driver`。
- 基于 Tkinter 的小车图形遥控器 `cmd_vel_gui`。
- 前进、后退、左转、右转和停车控制。
- 单次、连续及停止速度指令测试脚本。
- micro-ROS Agent UDP 启动脚本。
- ROS 2 Launch 文件与参数配置文件。
- `/odom` 订阅接口预留。
- 构建、启动和常见故障排查文档。

当前 ESP32 端主要订阅 `/cmd_vel`。里程计、TF、IMU、编码器反馈、SLAM 和 Nav2 尚未在本仓库中形成完整闭环。

## 3. 技术栈

| 类别 | 技术 |
| --- | --- |
| 操作系统 | Ubuntu / NVIDIA Jetson Linux |
| 机器人框架 | ROS 2 Humble |
| 上位机语言 | Python 3 |
| ROS 2 客户端库 | `rclpy` |
| 嵌入式通信 | micro-ROS |
| 底层控制器 | ESP32 |
| 网络传输 | UDP，默认端口 `8888` |
| 速度消息 | `geometry_msgs/msg/Twist` |
| 里程计消息 | `nav_msgs/msg/Odometry` |
| 图形界面 | Tkinter |
| 构建工具 | colcon / ament_python |

## 4. 目录结构

```text
akman-carbot-ros2-jetson/
├── README.md
├── PROJECT_DESCRIPTION_CN.md
├── STARTUP_PROCEDURE_CN.md
├── ROS2_HUMBLE_INSTALL_PROCEDURE.md
├── ROS2_HUMBLE_USAGE.md
├── MICRO_ROS_AGENT_SETUP_PROCEDURE.md
├── MICRO_ROS_HOST_SETUP.md
├── scripts/
│   ├── pub_cmd_vel_once.sh
│   ├── pub_cmd_vel_stream.sh
│   ├── pub_cmd_vel_stop.sh
│   ├── start_cmd_vel_gui.sh
│   └── start_micro_ros_agent_udp.sh
└── src/
    └── carbot_control/
        ├── package.xml
        ├── setup.py
        ├── setup.cfg
        ├── resource/
        ├── config/
        │   └── carbot.yaml
        ├── launch/
        │   └── carbot.launch.py
        └── carbot_control/
            ├── __init__.py
            ├── carbot_driver.py
            └── cmd_vel_gui.py
```

`build/`、`install/` 和 `log/` 是 colcon 在本机构建时生成的目录，不应作为源代码提交。

## 5. ROS 2 节点说明

### 5.1 `carbot_driver`

`carbot_driver` 是一个基础运动指令发布节点。它读取 ROS 参数并按固定周期向 `/cmd_vel` 发布 `Twist` 消息，同时订阅 `/odom` 并在调试日志中输出小车位置。

默认参数如下：

| 参数 | 默认值 | 含义 |
| --- | ---: | --- |
| `linear_speed` | `0.40` | X 方向线速度，单位 m/s |
| `angular_speed` | `0.0` | Z 轴角速度，单位 rad/s |
| `publish_period` | `0.2` | 发布周期，单位秒 |

默认配置相当于以 5 Hz 持续发布直行速度命令。

### 5.2 `cmd_vel_gui`

`cmd_vel_gui` 提供简单的桌面遥控界面，并支持鼠标按钮和键盘方向键：

- 按住 `Forward` 或上方向键：前进。
- 按住 `Backward` 或下方向键：后退。
- 按住 `Left` 或左方向键：左转。
- 按住 `Right` 或右方向键：右转。
- 松开方向键或方向按钮：停车。
- 点击红色 `STOP` 按钮或按空格键：立即停车。

GUI 默认以 10 Hz 持续发布当前运动命令，避免只发送一次命令后底层控制状态不明确。

## 6. ROS Topic 与数据约定

### `/cmd_vel`

- 消息类型：`geometry_msgs/msg/Twist`
- 方向：上位机控制节点 → ESP32
- `linear.x`：前后线速度，正值前进，负值后退。
- `angular.z`：转向角速度，正值左转，负值右转。

示例：

```yaml
linear:
  x: 0.40
  y: 0.0
  z: 0.0
angular:
  x: 0.0
  y: 0.0
  z: 0.0
```

### `/odom`

- 消息类型：`nav_msgs/msg/Odometry`
- 方向：底盘或里程计节点 → 上位机节点
- 当前状态：上位机已经预留订阅逻辑，ESP32 端尚需补充实际发布和坐标系定义。

## 7. 环境要求

建议环境：

- Ubuntu 22.04 或对应的 Jetson 系统环境。
- ROS 2 Humble 已安装到 `/opt/ros/humble`。
- Python 3 和 Tkinter。
- colcon 构建工具。
- 已单独构建的 micro-ROS Agent 工作空间。
- ESP32 与上位机连接到同一个局域网。

ESP32 固件需要配置：

```text
agent_ip   = 上位机当前局域网 IPv4 地址
agent_port = 8888
```

不要将文档中的历史 IP 地址当作固定配置。上位机网络变化后，应重新检查当前 IP 并同步修改 ESP32 固件配置。

## 8. 构建项目

在项目根目录执行：

```bash
source /opt/ros/humble/setup.bash
colcon build --packages-select carbot_control
source install/setup.bash
```

修改 Python 节点、Launch 文件或配置后，需要重新构建并重新加载工作空间环境。

## 9. 启动流程

### 第一步：启动 micro-ROS Agent

```bash
./scripts/start_micro_ros_agent_udp.sh
```

指定端口时：

```bash
./scripts/start_micro_ros_agent_udp.sh 8888
```

### 第二步：启动或重启 ESP32

建议先让 Agent 进入监听状态，再启动 ESP32。连接成功后，Agent 终端应出现 client 或 session 相关日志。

### 第三步：发送低速测试命令

```bash
./scripts/pub_cmd_vel_once.sh 0.10 0.0
```

确认小车运动方向和电机接线正确后，再逐步提高速度。

### 第四步：显式停车

```bash
./scripts/pub_cmd_vel_stop.sh
```

## 10. 控制方式

### 使用 GUI

```bash
./scripts/start_cmd_vel_gui.sh
```

也可以覆盖默认参数：

```bash
ros2 run carbot_control cmd_vel_gui --ros-args \
  -p linear_speed:=0.10 \
  -p angular_speed:=0.60 \
  -p publish_rate_hz:=10.0
```

### 使用 Launch 文件

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch carbot_control carbot.launch.py
```

### 使用测试脚本

```bash
# 单次前进
./scripts/pub_cmd_vel_once.sh 0.10 0.0

# 以 10 Hz 持续前进
./scripts/pub_cmd_vel_stream.sh 0.10 0.0 10

# 左转
./scripts/pub_cmd_vel_stream.sh 0.10 0.60 10

# 右转
./scripts/pub_cmd_vel_stream.sh 0.10 -0.60 10

# 停车
./scripts/pub_cmd_vel_stop.sh
```

## 11. 运行状态检查

常用 ROS 2 检查命令：

```bash
ros2 node list
ros2 topic list
ros2 topic info /cmd_vel
ros2 topic echo /cmd_vel
ros2 param list
```

如果 ESP32 没有响应，按以下顺序检查：

1. 上位机和 ESP32 是否位于同一局域网。
2. ESP32 的 `agent_ip` 是否为上位机当前 IP。
3. ESP32 的端口是否与 Agent 监听端口一致。
4. micro-ROS Agent 是否先于 ESP32 启动。
5. Agent 终端是否出现客户端连接日志。
6. `/cmd_vel` 是否确实存在发布者和订阅者。
7. 电机驱动供电、使能信号和接线是否正确。
8. 是否使用了足够低且安全的测试速度。

## 12. 安全注意事项

- 第一次联调时应架空驱动轮，确认方向正确后再落地测试。
- 优先使用低速参数，避免小车突然启动。
- 测试结束后显式发送零速度命令。
- GUI 关闭时会发送停车命令，但不应将软件停车作为唯一安全措施。
- 建议 ESP32 固件实现速度命令超时保护：在限定时间内未收到新指令时自动停车。
- 确保现场具备物理断电或急停手段。
- 不要让多个控制节点在没有仲裁机制的情况下同时发布 `/cmd_vel`。

## 13. 当前限制

- 仓库主要包含 ROS 2 上位机代码，ESP32 固件不在当前源码树中。
- `/cmd_vel` 控制仍属于开环控制，缺少编码器闭环速度反馈。
- `/odom` 只有订阅入口，尚无完整数据来源。
- 尚未建立 `odom`、`base_link`、传感器坐标系之间的 TF tree。
- 尚未集成机器人模型 URDF/Xacro。
- 尚未集成 IMU、相机或激光雷达数据。
- 尚未集成 SLAM、定位、路径规划和 Nav2。
- 目前没有控制权仲裁、自动急停和完整的硬件在环测试。

## 14. 后续规划

建议按照以下顺序扩展：

1. 在 ESP32 端加入 `/cmd_vel` 超时停车保护。
2. 接入编码器并实现轮速闭环 PID。
3. 发布 `/odom` 并补齐 `odom → base_link` TF。
4. 添加 URDF/Xacro 机器人模型和 `robot_state_publisher`。
5. 接入 IMU，并使用 `robot_localization` 融合里程计。
6. 接入相机或激光雷达。
7. 集成 SLAM 与 Nav2，实现建图、定位和自主导航。
8. 增加自动化测试、设备健康检查和启动编排。

## 15. 设计价值

项目当前规模不大，但已经建立了可扩展机器人的核心接口边界：

- 使用标准 ROS 2 Topic，而不是为每种控制方式设计私有协议。
- 使用 micro-ROS 连接资源受限的嵌入式控制器。
- 将 GUI、测试工具、自动控制节点和底盘执行层解耦。
- 使用参数、Launch 和脚本管理运行配置。
- 保持 Python 上位机包便于快速实验，未来可并行增加 C++ 高频控制包。

因此，后续无论加入手柄遥控、视觉跟随、路径规划还是 Nav2，底层 ESP32 都可以继续围绕 `/cmd_vel` 接口工作，无需随控制来源反复修改通信协议。

## 16. License

本项目使用 MIT License。实际发布前请确认仓库中包含完整的 `LICENSE` 文件，并核对第三方组件各自的许可证要求。
