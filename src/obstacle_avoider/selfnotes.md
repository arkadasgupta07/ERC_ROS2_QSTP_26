1. Core Executable Elements

Node
Definition: An executable process dedicated to a single, focused task (e.g., driving wheel motors, processing camera frames, or running pathfinding).
Why Use It: Keeps code modular and fault-tolerant. If your camera node crashes, your motor control node continues running safely without freezing the entire system.

Message
Definition: The strict data structure or layout used to package information before transmitting it across the network.
Why Use It: Guarantees data compatibility across nodes. For instance, geometry_msgs/msg/Twist strictly defines 3D linear and angular velocity fields ($x, y, z$).

------------------------------------------------------------------------

2. Topic Architecture (1-Way Streaming)

Topic
An open, named bus channel. Publishers send data into it without needing to know which nodes receive it, and Subscribers listen without needing to know which node sent it.

Publisher
The active sender component inside a Node that pushes Messages onto a Topic at regular time intervals.

Subscriber
The active receiver component inside a Node that listens to a Topic and triggers a callback function whenever a new Message arrives.

Primary Use Case: Continuous, high-speed streaming data loops where high update frequency is required (e.g., 30 Hz LiDAR scan feeds or constant motor velocity commands).

------------------------------------------------------------------------

3. Service Architecture (2-Way Request/Response)

Service
Definition: A client-server interaction model where a Client node sends a Request and waits until the Server node executes the task and sends back a Response.

Primary Use Case: Intermittent, discrete operations that require confirmation—such as toggling an ON/OFF state switch (/toggle_robot), triggering system calibration, or saving a map file.

------------------------------------------------------------------------

4. Key Distinction: Topic vs. Service
Core Rule of Thumb: Use Topics for continuous, asynchronous data streams where dropping a single frame won't break the system (e.g., sensor feeds, teleop controls).Use Services for quick, discrete actions that require immediate confirmation or state verification (e.g., mode switches, hardware resets).


------------------------------------------------------------------------------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------------------------------------------------------------------------------

ros2 topic echo /scan

What it does: Prints the raw, real-time data stream passing through the /scan topic onto your screen.
Why use it: Debugging. It lets you visually inspect incoming LiDAR distance arrays (ranges), intensity values, and header timestamps live as the robot senses its environment.

header:
  stamp:
    sec: 1724
    nanosec: 450000000
  frame_id: base_scan
angle_min: -3.1415927410125732
angle_max: 3.1415927410125732
angle_increment: 0.01745329238474369
time_increment: 0.0
scan_time: 0.0
range_min: 0.12000000476837158
range_max: 3.5
ranges:
- 1.2450000047683716
- 1.241000056028366
- 1.2389999628067017
- '... (357 more float values representing 360 degrees) ...'
intensities: []
---

------------------------------------------------------------------------

ros2 topic info /scan

What it does: Displays metadata about the topic, including its strict message type (sensor_msgs/msg/LaserScan), active publisher count, and subscriber count.
Why use it: Connectivity checks. It tells you if the simulation node publishing sensor data and your python node receiving it are actually connected on the same bus.

Type: sensor_msgs/msg/LaserScan
Publisher count: 1
Subscription count: 1

------------------------------------------------------------------------

ros2 interface show geometry_msgs/msg/Twist

This expresses velocity in free space broken into its linear and angular parts.
What it does: Reveals the internal variable structure and field definitions of a specific ROS 2 message interface.Why use it: Syntax lookup. Running this shows that a Twist message contains Vector3 linear ($x, y, z$) and Vector3 angular ($x, y, z$) floating-point fields, telling you exactly which attributes to access in your Python code (cmd.linear.x = 0.2).

Vector3  linear
	float64 x
	float64 y
	float64 z
Vector3  angular
	float64 x
	float64 y
	float64 z

  
------------------------------------------------------------------------

ros2 service list

What it does: Outputs a complete list of all synchronous service endpoints currently registered across all active nodes in the ROS 2 graph.
Why use it: Discovery. It verifies that your node successfully hosted its service endpoint (like /toggle_robot) so you know what path to target when executing ros2 service call.

/obstacle_avoider/describe_parameters
/obstacle_avoider/get_parameter_types
/obstacle_avoider/get_parameters
/obstacle_avoider/list_parameters
/obstacle_avoider/set_parameters
/toggle_robot



