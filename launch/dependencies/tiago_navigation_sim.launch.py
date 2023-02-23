# Copyright (c) 2018 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Modified by José Miguel Guerrero Hernández

import os
import yaml

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import SetRemap


def generate_launch_description():

    # Get the launch directory
    robots_dir = get_package_share_directory('robocup2023')
    bringup_dir = get_package_share_directory('nav2_bringup')

    # Create the launch configuration variables
    params_file = LaunchConfiguration('params_file')
    slam = LaunchConfiguration('slam')
    map_yaml_file = LaunchConfiguration('map')
    use_sim_time = LaunchConfiguration('use_sim_time')
    slam_params_file = LaunchConfiguration('slam_params_file')
    autostart = LaunchConfiguration('autostart')
    rviz_config_file = LaunchConfiguration('rviz_config_file')

    # Declare the launch arguments
    declare_params_file_cmd = DeclareLaunchArgument(
        'params_file',
        default_value=os.path.join(robots_dir, 'params', 'tiago_nav_params_sim.yaml'),
        description='Full path to the ROS2 parameters file to use for all launched nodes')

    declare_slam_params_file_cmd = DeclareLaunchArgument(
        'slam_params_file',
        default_value=os.path.join(robots_dir, 'params', 'mapper_params_online_async.yaml'),
        description='Full path to the ROS2 parameters file to use for all launched nodes')

    declare_slam_cmd = DeclareLaunchArgument(
        'slam',
        default_value='False',
        description='Whether run a SLAM')

    config = os.path.join(robots_dir, 'config', 'params.yaml')

    with open(config, "r") as stream:
        try:
            conf = (yaml.safe_load(stream))

        except yaml.YAMLError as exc:
            print(exc)

    declare_map_yaml_cmd = DeclareLaunchArgument(
        'map',
        default_value=os.path.join(robots_dir, 'maps', conf['robocup2023']['world']+'.yaml'),
        description='Full path to map yaml file to load')

    declare_use_sim_time_cmd = DeclareLaunchArgument(
        'use_sim_time',
        default_value='True',
        description='Use simulation (Gazebo) clock if true')

    declare_autostart_cmd = DeclareLaunchArgument(
        'autostart', default_value='true',
        description='Automatically startup the nav2 stack')

    nav2_bringup_cmd_group = GroupAction([
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(bringup_dir, 'launch', 'online_async_launch.py')),
            condition=IfCondition(slam),
            launch_arguments={'use_sim_time': use_sim_time,
                              'autostart': autostart,
                              'slam_params_file': slam_params_file}.items())

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(bringup_dir, 'launch',
                                                       'localization_launch.py')),
            condition=IfCondition(PythonExpression(['not ', slam])),
            launch_arguments={'map': map_yaml_file,
                              'use_sim_time': use_sim_time,
                              'autostart': autostart,
                              'params_file': params_file,
                              'use_lifecycle_mgr': 'false'}.items()),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(robots_dir, 'launch',
                                          'dependencies', 'navigation_launch_sim.py')),
            launch_arguments={'use_sim_time': use_sim_time,
                              'autostart': autostart,
                              'params_file': params_file,
                              'use_lifecycle_mgr': 'false',
                              'map_subscribe_transient_local': 'true'}.items()),
    ])

    declare_rviz_config_file_cmd = DeclareLaunchArgument(
        'rviz_config_file',
        default_value=os.path.join(bringup_dir, 'rviz', 'nav2_default_view.rviz'),
        description='Full path to the RVIZ config file to use')

    declare_use_rviz_cmd = DeclareLaunchArgument(
        'use_rviz',
        default_value='True',
        description='Whether to start RVIZ')

    rviz_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(bringup_dir, 'launch', 'rviz_launch.py')),
        launch_arguments={'rviz_config': rviz_config_file}.items())

    # Remapping
    scan_remap = SetRemap(src='scan', dst='scan_raw')

    # Create the launch description and populate
    ld = LaunchDescription()

    # Declare the launch options
    ld.add_action(scan_remap)
    ld.add_action(declare_params_file_cmd)
    ld.add_action(declare_slam_params_file_cmd)
    ld.add_action(declare_slam_cmd)
    ld.add_action(declare_map_yaml_cmd)
    ld.add_action(declare_use_sim_time_cmd)
    ld.add_action(declare_autostart_cmd)
    ld.add_action(declare_rviz_config_file_cmd)
    ld.add_action(declare_use_rviz_cmd)
    ld.add_action(nav2_bringup_cmd_group)
    ld.add_action(rviz_cmd)

    return ld
