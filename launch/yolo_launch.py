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
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    yolo_dir = get_package_share_directory('yolov8_bringup')
    perception_dir = get_package_share_directory('perception_2d_to_3d')
    camera_dir = get_package_share_directory('astra_camera')

    yolo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(yolo_dir,'launch', 'yolov8.launch.py')),
        launch_arguments={'input_image_topic': '/camera/color/image_raw',
                          'threshold':'0.6'}.items())  # change to /xtion/rgb/image_raw

    perception_3d = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(perception_dir, 'launch', 'perception_2d_to_3d.launch.py')),
        launch_arguments={'camera_depth_info_topic': '/camera/depth/camera_info', # change to /xtion/depth/image_raw
                          'depth_image_raw_topic': '/camera/depth/image_raw'}.items() # change to /xtion/depth/camera_info
        )
    camera = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(camera_dir, 'launch', 'astra_mini.launch.py'))
        )
    


    ld = LaunchDescription()


    ld.add_action(yolo)
    ld.add_action(perception_3d)
    ld.add_action(camera)


    return ld
