# ROS 2 Humble 使用笔记

这是一份面向当前机器和 `carbot-ros2` 工作空间的 ROS 2 Humble 常用命令参考。

## 环境加载

新的 bash 终端会自动加载 ROS 2 Humble，因为 `~/.bashrc` 中已经加入：

```bash
source /opt/ros/humble/setup.bash
```

如果是在已经打开的旧终端中，可以手动执行：

```bash
source /opt/ros/humble/setup.bash
```

工作空间 build 之后，还需要加载当前工作空间的 overlay：

```bash
source install/setup.bash
```

## 构建当前工作空间

```bash
cd ~/Projects/carbot-ros2
source /opt/ros/humble/setup.bash
rosdep install --from-paths src --ignore-src -r -y
colcon build
source install/setup.bash
```

## 运行 Carbot

```bash
cd ~/Projects/carbot-ros2
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch carbot_control carbot.launch.py
```

## 常用 ROS 2 命令

列出所有 package：

```bash
ros2 pkg list
```

查找 package 的安装路径：

```bash
ros2 pkg prefix rclpy
ros2 pkg prefix carbot_control
```

列出正在运行的 node：

```bash
ros2 node list
```

查看 node 信息：

```bash
ros2 node info /carbot_driver
```

列出 topic：

```bash
ros2 topic list
```

查看 topic 类型：

```bash
ros2 topic info /cmd_vel
```

监听 topic：

```bash
ros2 topic echo /cmd_vel
```

发布速度命令：

```bash
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.40}, angular: {z: 0.0}}"
```

列出 service：

```bash
ros2 service list
```

列出 parameter：

```bash
ros2 param list
```

读取 parameter：

```bash
ros2 param get /carbot_driver linear_speed
```

设置 parameter：

```bash
ros2 param set /carbot_driver linear_speed 0.4
```

## Launch 文件

运行 launch 文件：

```bash
ros2 launch carbot_control carbot.launch.py
```

查看 launch 参数：

```bash
ros2 launch carbot_control carbot.launch.py --show-args
```

## 构建命令

构建整个工作空间：

```bash
colcon build
```

只构建一个 package：

```bash
colcon build --packages-select carbot_control
```

清理本地构建产物：

```bash
rm -rf build install log
```

重新构建：

```bash
colcon build
source install/setup.bash
```

## 依赖管理

安装 `src` 中所有 package 的系统依赖：

```bash
rosdep install --from-paths src --ignore-src -r -y
```

更新 rosdep 元数据：

```bash
rosdep update
```

## 常用 Demo

运行 ROS 2 talker：

```bash
ros2 run demo_nodes_cpp talker
```

在另一个终端运行 listener：

```bash
ros2 run demo_nodes_py listener
```

运行 turtlesim：

```bash
ros2 run turtlesim turtlesim_node
```

在另一个终端用键盘控制 turtlesim：

```bash
ros2 run turtlesim turtle_teleop_key
```

## 排错

如果提示找不到 `ros2`：

```bash
source /opt/ros/humble/setup.bash
```

如果找不到当前工作空间中的 package：

```bash
cd ~/Projects/carbot-ros2
source install/setup.bash
```

如果依赖缺失：

```bash
cd ~/Projects/carbot-ros2
rosdep install --from-paths src --ignore-src -r -y
```

如果修改 package metadata 后 build 表现异常：

```bash
cd ~/Projects/carbot-ros2
rm -rf build install log
colcon build
source install/setup.bash
```

如果 ROS node 之间无法通信，先检查：

```bash
echo $ROS_DOMAIN_ID
ros2 node list
ros2 topic list
```

单机开发时，`ROS_DOMAIN_ID` 通常可以保持未设置。多机器人或多人共享网络时，需要让需要通信的终端使用相同的 domain ID：

```bash
export ROS_DOMAIN_ID=10
```
