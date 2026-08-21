#!/usr/bin/env python3
import math
import os
import time
import yaml

from ament_index_python.packages import get_package_share_directory
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
import rclpy
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from waypoint_follower.action import Mission


def get_yaw_from_quaternion(q):
    siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
    cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
    return math.atan2(siny_cosp, cosy_cosp)


class MissionServerNode(Node):

    def __init__(self):
        super().__init__('mission_server')

        self.current_x = 0.0
        self.current_y = 0.0
        self.current_yaw = 0.0

        # Allows callbacks (/odom and execute_callback) to run concurrently
        self.cb_group = ReentrantCallbackGroup()

        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.odom_sub = self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            10,
            callback_group=self.cb_group,
        )

        self._action_server = ActionServer(
            self,
            Mission,
            'follow_mission',
            execute_callback=self.execute_callback,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback,
            callback_group=self.cb_group,
        )
        self.get_logger().info('Mission Action Server Initialized.')

    def odom_callback(self, msg):
        self.current_x = msg.pose.pose.position.x
        self.current_y = msg.pose.pose.position.y
        self.current_yaw = get_yaw_from_quaternion(msg.pose.pose.orientation)

    def goal_callback(self, goal_request):
        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle):
        self.get_logger().info('Cancel request received!')
        return CancelResponse.ACCEPT

    def execute_callback(self, goal_handle):
        feedback_msg = Mission.Feedback()
        result = Mission.Result()

        mission_filename = goal_handle.request.mission_file
        pkg_share = get_package_share_directory('waypoint_follower')
        yaml_path = os.path.join(pkg_share, 'missions', mission_filename)

        if not os.path.exists(yaml_path):
            self.get_logger().error(f'File not found: {yaml_path}')
            goal_handle.abort()
            result.success = False
            return result

        with open(yaml_path, 'r') as f:
            mission_data = yaml.safe_load(f)

        targets = list(mission_data.get('waypoints', []))
        if mission_data.get('return_to_base', False):
            targets.append(mission_data.get('base', {'x': 0.0, 'y': 0.0}))

        total_distance = 0.0
        waypoints_completed = 0

        for idx, target in enumerate(targets):
            target_x = target['x']
            target_y = target['y']
            is_returning = idx == len(targets) - 1 and mission_data.get(
                'return_to_base', False
            )

            while rclpy.ok():
                if goal_handle.is_cancel_requested:
                    self.cmd_pub.publish(Twist())
                    goal_handle.canceled()
                    self.get_logger().info('Mission canceled successfully.')
                    result.success = False
                    result.total_distance = float(total_distance)
                    result.waypoints_completed = waypoints_completed
                    return result

                dx = target_x - self.current_x
                dy = target_y - self.current_y
                dist = math.hypot(dx, dy)

                if dist < 0.15:  # Reached waypoint threshold
                    self.cmd_pub.publish(Twist())
                    if not is_returning:
                        waypoints_completed += 1
                    break

                desired_yaw = math.atan2(dy, dx)
                yaw_error = desired_yaw - self.current_yaw
                yaw_error = math.atan2(
                    math.sin(yaw_error), math.cos(yaw_error)
                )

                cmd = Twist()
                if abs(yaw_error) > 0.2:
                    cmd.angular.z = 0.5 if yaw_error > 0 else -0.5
                else:
                    cmd.linear.x = min(0.2, 0.5 * dist)
                    cmd.angular.z = 1.0 * yaw_error

                self.cmd_pub.publish(cmd)
                total_distance += 0.02 * cmd.linear.x

                feedback_msg.current_waypoint_index = idx
                feedback_msg.status = (
                    'Returning to base'
                    if is_returning
                    else f'En route to waypoint {idx+1}/{len(targets)}'
                )
                feedback_msg.distance_to_target = float(dist)
                goal_handle.publish_feedback(feedback_msg)

                time.sleep(0.05)

        self.cmd_pub.publish(Twist())
        goal_handle.succeed()
        result.success = True
        result.total_distance = float(total_distance)
        result.waypoints_completed = waypoints_completed
        return result


def main(args=None):
    rclpy.init(args=args)
    node = MissionServerNode()

    # MultiThreadedExecutor allows odom_callback and execute_callback to run in parallel threads
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
