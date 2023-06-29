# Copyright (c) 2022 PAL Robotics S.L. All rights reserved.
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

import os
import yaml

from os import environ, pathsep

from ament_index_python.packages import get_package_prefix, get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

from launch_pal.include_utils import include_launch_py_description


from launch_ros.actions import Node


def get_model_paths(packages_names):
    model_paths = ''
    for package_name in packages_names:
        if model_paths != '':
            model_paths += pathsep

        package_path = get_package_prefix(package_name)
        model_path = os.path.join(package_path, 'share')

        model_paths += model_path

    return model_paths


def get_resource_paths(packages_names):
    resource_paths = ''
    for package_name in packages_names:
        if resource_paths != '':
            resource_paths += pathsep

        package_path = get_package_prefix(package_name)
        resource_paths += package_path

    return resource_paths


def generate_launch_description():

    robots_dir = get_package_share_directory('robocup2023')

    config = os.path.join(robots_dir, 'config', 'params.yaml')
    with open(config, "r") as stream:
        try:
            conf = (yaml.safe_load(stream))

        except yaml.YAMLError as exc:
            print(exc)

    navigation_arg = DeclareLaunchArgument(
        'navigation', default_value='false',
        description='Specify if launching Navigation2'
    )

    moveit_arg = DeclareLaunchArgument(
        'moveit', default_value='false',
        description='Specify if launching MoveIt2'
    )


    world_name_arg = DeclareLaunchArgument(
        'world_name', default_value='pal_office',
        description="Specify world name, we'll convert to full path"
    )

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('gazebo_ros'),
            'launch'), '/gazebo.launch.py']),
        launch_arguments={'gui': str(conf['robocup2023']['gazebo_gui']),
                          }.items())

    tiago_spawn = include_launch_py_description(
        'tiago_gazebo', ['launch', 'tiago_spawn.launch.py'])

    tiago_bringup = include_launch_py_description(
        'tiago_bringup', ['launch', 'tiago_bringup.launch.py'])

    navigation = include_launch_py_description(
        'tiago_2dnav', ['launch', 'tiago_sim_nav_bringup.launch.py'],
        condition=IfCondition(LaunchConfiguration('navigation')))

    move_group = include_launch_py_description(
        'tiago_moveit_config', ['launch', 'move_group.launch.py'],
        condition=IfCondition(LaunchConfiguration('moveit')))

    tuck_arm = Node(package='tiago_gazebo',
                    executable='tuck_arm.py',
                    emulate_tty=True,
                    output='both')

    # @TODO: review pal_gazebo
    # @TODO: review tiago_spawn
    # @TODO: simulation_tiago_bringup?
    # @TODO: pal_pcl_points_throttle_and_filter

    packages = ['tiago_description', 'pmb2_description',
                'hey5_description', 'pal_gripper_description']
    model_path = get_model_paths(packages)
    resource_path = get_resource_paths(packages)

    if 'GAZEBO_MODEL_PATH' in environ:
        model_path += pathsep + environ['GAZEBO_MODEL_PATH']

    if 'GAZEBO_RESOURCE_PATH' in environ:
        resource_path += pathsep + environ['GAZEBO_RESOURCE_PATH']

    # Create the launch description and populate
    ld = LaunchDescription()

    ld.add_action(SetEnvironmentVariable('GAZEBO_MODEL_PATH', model_path))
    # Using this prevents shared library from being found
    # ld.add_action(SetEnvironmentVariable('GAZEBO_RESOURCE_PATH', tiago_resource_path))

    ld.add_action(world_name_arg)
    ld.add_action(gazebo)
    ld.add_action(tiago_spawn)
    ld.add_action(tiago_bringup)

    ld.add_action(navigation_arg)
    ld.add_action(navigation)

    ld.add_action(moveit_arg)
    ld.add_action(move_group)
    # ld.add_action(tuck_arm)

    return ld