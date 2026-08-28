from glob import glob
from setuptools import setup

package_name = "carbot_control"

setup(
    name=package_name,
    version="0.1.0",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml"]),
        (f"share/{package_name}/launch", glob("launch/*.launch.py")),
        (f"share/{package_name}/config", glob("config/*.yaml")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="shenfq",
    maintainer_email="shenfq@example.com",
    description="Starter ROS 2 Humble control package for carbot.",
    license="MIT",
    entry_points={
        "console_scripts": [
            "carbot_driver = carbot_control.carbot_driver:main",
            "cmd_vel_gui = carbot_control.cmd_vel_gui:main",
        ],
    },
)
