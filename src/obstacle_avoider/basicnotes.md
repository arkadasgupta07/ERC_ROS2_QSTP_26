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
