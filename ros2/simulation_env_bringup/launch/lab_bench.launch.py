"""Launch the lab-bench world in Gazebo Sim and bridge it to ROS 2.

    ros2 launch simulation_env_bringup lab_bench.launch.py
    ros2 launch simulation_env_bringup lab_bench.launch.py gui:=false
    ros2 launch simulation_env_bringup lab_bench.launch.py paused:=true

Drive the rail carriage (metres, +/-0.42 from centre):

    ros2 topic pub --once /rail_axis/carriage_slide/cmd_pos \
        std_msgs/msg/Float64 "{data: 0.30}"
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (DeclareLaunchArgument, IncludeLaunchDescription,
                            SetEnvironmentVariable)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node


def generate_launch_description():
    pkg = get_package_share_directory('simulation_env_bringup')
    models = os.path.join(pkg, 'gazebo', 'models')
    world = os.path.join(pkg, 'gazebo', 'worlds', 'lab_bench.world')
    bridge_config = os.path.join(pkg, 'config', 'ros_gz_bridge.yaml')

    existing = os.environ.get('GZ_SIM_RESOURCE_PATH', '')
    resource_path = models + (os.pathsep + existing if existing else '')

    gui = LaunchConfiguration('gui')
    paused = LaunchConfiguration('paused')

    # "-r" runs immediately, "-s" is server-only (no GUI)
    gz_args = PythonExpression([
        "'", world, "'",
        " + ('' if '", paused, "' == 'true' else ' -r')",
        " + ('' if '", gui, "' == 'true' else ' -s')",
    ])

    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(
            get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')),
        launch_arguments={'gz_args': gz_args}.items(),
    )

    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='lab_bench_bridge',
        parameters=[{'config_file': bridge_config,
                     'use_sim_time': True}],
        output='screen',
    )

    return LaunchDescription([
        DeclareLaunchArgument('gui', default_value='true',
                              description='run the Gazebo GUI'),
        DeclareLaunchArgument('paused', default_value='false',
                              description='start paused instead of running'),
        SetEnvironmentVariable('GZ_SIM_RESOURCE_PATH', resource_path),
        gz_sim,
        bridge,
    ])
