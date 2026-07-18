# ERC ROS 2 QSTP 2026 - Week 0 Assignment

This repository contains the foundational environment setup and the implementation of my first custom ROS 2 package: **The Echo Chamber**.

---

## 📁 Repository Structure
* **`echo_chamber/`**: Custom ROS 2 Python package containing the publisher and subscriber nodes.
  * `talker.py`: Publishes a random float between 0.0 and 100.0 to the `/random_number` topic at 1.0 Hz.
  * `listener.py`: Subscribes to `/random_number`, multiplies the data by 2, and logs the output.
* **`demo.webm`**: Screen recording demonstrating the node communication.

---

## 🎥 Video Demonstration
Below is the screen recording showing the nodes successfully communicating in real time:

<video src="demo.webm" width="100%" controls></video>

---

## 🚀 How to Run the Nodes

1. **Build the workspace:**
   ```bash
   cd ~/qstp_ws
   colcon build