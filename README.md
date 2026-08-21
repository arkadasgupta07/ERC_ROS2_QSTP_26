# ERC ROS 2 QSTP 2026 - Master Repository

This repository contains my progress, assignments, and custom ROS 2 packages developed during the **ERC ROS 2 QSTP 2026** program.

---

## 🚀 Repository Structure

| Package | Week | Core Concepts |
| :--- | :--- | :--- |
| **`echo_chamber`** | Week 0 | Publishers, Subscribers, `rclpy` Node Lifecycle |
| **`obstacle_avoider`** | Week 1 | LaserScan Data Processing, Service Servers (`std_srvs`), Twist Velocity Control |
| **`waypoint_follower`** | Week 2 | ROS 2 Actions (`.action`), Multithreaded Executors, `ReentrantCallbackGroup`, Quaternion Kinematics |

---

## ⚙️ Prerequisites & Setup

Before running any package, build the workspace and source the environment:

```bash
cd ~/qstp_ws
colcon build
source install/setup.bash
```
---
---

# 📌 Week 0: Echo Chamber
### Objective: 
Implement foundational publisher and subscriber nodes using Python (rclpy).

### Components:

**talker.py:** Publishes a random float between 0.0 and 100.0 to the /random_number topic at 1.0 Hz.

**listener.py:** Subscribes to /random_number, multiplies incoming values by 2, and logs the output.

### Demonstration Video:-
Watch Week 0 Demo
[ERC_ROS2_QSTP_2026_Week0.webm](https://github.com/user-attachments/assets/a2def97e-2f61-45d2-8b40-974e3144dec5)

### How to Run Week 0
```Bash
# Terminal 1: Run Publisher Node
source ~/qstp_ws/install/setup.bash
ros2 run echo_chamber talker

# Terminal 2: Run Subscriber Node
source ~/qstp_ws/install/setup.bash
ros2 run echo_chamber listener
```

---

#  📌 Week 1: Obstacle Avoider
### Objective:
Program autonomous obstacle avoidance for a TurtleBot3 in a simulated Gazebo environment with service-based start/stop toggles.

### Components:

**avoider.py:** Subscribes to **/scan** (sensor_msgs/msg/LaserScan), filters range data, dynamically adjusts **/cmd_vel** steering commands, and provides a **/toggle_robot** service server (std_srvs/srv/SetBool).

### How to Run Week 1
```Bash
# Terminal 1: Launch Gazebo Simulation
source ~/qstp_ws/install/setup.bash
export TURTLEBOT3_MODEL=waffle
ros2 launch turtlebot3_gz_sim bringup.launch.py world:=obstacle.sdf

# Terminal 2: Run Obstacle Avoider Node
source ~/qstp_ws/install/setup.bash
ros2 run obstacle_avoider avoider

# Terminal 3: Toggle Robot On / Off via Service Calls
source ~/qstp_ws/install/setup.bash

# Start robot movement:
ros2 service call /toggle_robot std_srvs/srv/SetBool "{data: true}"

# Stop robot movement:
ros2 service call /toggle_robot std_srvs/srv/SetBool "{data: false}"
```

### Demonstration Video Link:- https://drive.google.com/file/d/1P_SQ0G3kkyYsJi_APPHwHM_MVHvpqB78/view?usp=sharing

---

#  📌 Week 2: Waypoint Follower (ROS 2 Action Server & Client)
### Objective:
Build an asynchronous ROS 2 Action Server and Client that executes multi-waypoint missions loaded from YAML configuration files, featuring live feedback and mid-mission cancellation.

### Key Features:

**Custom Action Interface:** Mission.action defining Goal (mission_file), Result (success, total_distance, waypoints_completed), and Feedback (current_waypoint_index, status, distance_to_target).

**Multithreading:** Implements ReentrantCallbackGroup and MultiThreadedExecutor to keep /odom callbacks responsive while execution loops process commands.

**Kinematic Control:** Converts Odometry quaternions to Euler Yaw angles to calculate proportional heading errors and linear distance targets.

###  How to Run Week 2
```Bash
# Terminal 1: Launch Gazebo Simulation
source ~/qstp_ws/install/setup.bash
export TURTLEBOT3_MODEL=waffle
ros2 launch turtlebot3_gz_sim bringup.launch.py world:=obstacle.sdf

# Terminal 2: Start Action Server
source ~/qstp_ws/install/setup.bash
ros2 run waypoint_follower mission_server

# Terminal 3: Run Action Client
source ~/qstp_ws/install/setup.bash
ros2 run waypoint_follower mission_client mission_square.yaml
```

### Demonstration Video Link:- https://drive.google.com/file/d/122PFGDwM-4K9XDztPdRTc2fwbDUx6ne6/view?usp=sharing

---
---



