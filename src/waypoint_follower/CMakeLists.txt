cmake_minimum_required(VERSION 3.8)
project(waypoint_follower)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(rclpy REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(rosidl_default_generators REQUIRED)

# Compile the custom action interface
rosidl_generate_interfaces(${PROJECT_NAME}
  "action/Mission.action"
  DEPENDENCIES geometry_msgs nav_msgs
)

# Install Python scripts as executable CLI binaries without .py extension
install(PROGRAMS
  scripts/mission_server.py
  DESTINATION lib/${PROJECT_NAME}
  RENAME mission_server
)

install(PROGRAMS
  scripts/mission_client.py
  DESTINATION lib/${PROJECT_NAME}
  RENAME mission_client
)

# Install the mission configuration directory into share space
install(DIRECTORY
  missions
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
