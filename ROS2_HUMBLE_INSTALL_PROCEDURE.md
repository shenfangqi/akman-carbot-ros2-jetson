# ROS 2 Humble 安装过程记录

这份文档记录了在当前机器上安装 ROS 2 Humble 的实际步骤。

## 环境信息

- 用户：`shenfq`
- 系统：Ubuntu `22.04.5 LTS`
- 代号：`jammy`
- 架构：`arm64`
- ROS 版本：`humble`

## 安装步骤

1. 确认 Ubuntu 版本：

   ```bash
   lsb_release -a
   ```

2. 确认 ROS 2 尚未安装或未在当前 shell 中可用：

   ```bash
   command -v ros2
   dpkg -l ros-humble-desktop ros-dev-tools
   ```

3. 安装基础依赖：

   ```bash
   sudo apt update
   sudo apt install -y locales software-properties-common curl
   ```

4. 配置 UTF-8 locale：

   ```bash
   sudo locale-gen en_US en_US.UTF-8
   sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
   ```

5. 启用 Ubuntu Universe 软件源：

   ```bash
   sudo add-apt-repository -y universe
   ```

6. 安装官方 ROS 2 apt 源配置包：

   ```bash
   ROS_APT_SOURCE_VERSION=$(curl -s https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest \
     | grep -F "tag_name" \
     | awk -F'"' '{print $4}')

   curl -L -o /tmp/ros2-apt-source.deb \
     "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${ROS_APT_SOURCE_VERSION}/ros2-apt-source_${ROS_APT_SOURCE_VERSION}.$(. /etc/os-release && echo ${UBUNTU_CODENAME:-${VERSION_CODENAME}})_all.deb"

   sudo dpkg -i /tmp/ros2-apt-source.deb
   ```

7. 安装 ROS 2 前更新系统包：

   ```bash
   sudo apt update
   sudo apt upgrade -y
   ```

8. 安装 ROS 2 Humble Desktop 和开发工具：

   ```bash
   sudo apt install -y ros-humble-desktop ros-dev-tools
   ```

9. 将 ROS 2 Humble 环境加载命令加入 `~/.bashrc`：

   ```bash
   # ROS 2 Humble
   if [ -f /opt/ros/humble/setup.bash ]; then
       source /opt/ros/humble/setup.bash
   fi
   ```

10. 初始化并更新 `rosdep`：

    ```bash
    sudo rosdep init
    rosdep update
    ```

11. 验证关键 ROS 2 包和工具：

    ```bash
    source /opt/ros/humble/setup.bash
    ros2 pkg prefix rclpy
    ros2 pkg prefix geometry_msgs
    ros2 pkg prefix nav_msgs
    colcon --help
    ```

12. 验证 `carbot-ros2` 工作空间：

    ```bash
    cd ~/Projects/carbot-ros2
    source /opt/ros/humble/setup.bash
    rosdep install --from-paths src --ignore-src -r -y
    colcon build
    ```

## 已确认安装的包

使用下面命令检查：

```bash
dpkg -l ros-humble-desktop ros-dev-tools ros2-apt-source
```

已确认存在：

- `ros-humble-desktop`
- `ros-dev-tools`
- `ros2-apt-source`

## 备注

- 本次安装使用的是 ROS 2 Humble 官方 Ubuntu deb 包安装方式。
- 当前机器使用 Ubuntu Jammy，对应 ROS 软件源为 `packages.ros.org`。
- `rosdep update` 需要访问 `raw.githubusercontent.com` 下载依赖元数据。
- 在 Codex 沙盒中做 launch smoke test 时，`carbot_driver` 节点可以启动，但 DDS 创建 UDP socket 会被沙盒限制阻止。普通终端环境通常不会有这个限制。

官方参考文档：

https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debs.html
