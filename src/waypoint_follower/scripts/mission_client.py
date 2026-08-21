#!/usr/bin/env python3
import sys

import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from waypoint_follower.action import Mission


class MissionClientNode(Node):

    def __init__(self):
        super().__init__('mission_client')
        self._action_client = ActionClient(self, Mission, 'follow_mission')

    def send_goal(self, mission_file):
        goal_msg = Mission.Goal()
        goal_msg.mission_file = mission_file

        self._action_client.wait_for_server()
        self.get_logger().info(f'Sending goal with file: {mission_file}')

        self._send_goal_future = self._action_client.send_goal_async(
            goal_msg, feedback_callback=self.feedback_callback
        )
        return self._send_goal_future

    def feedback_callback(self, feedback_msg):
        fb = feedback_msg.feedback
        self.get_logger().info(
            f'[{fb.status}] Waypoint Index: {fb.current_waypoint_index} | Dist: {fb.distance_to_target:.2f}m'
        )


def main(args=None):
    rclpy.init(args=args)
    node = MissionClientNode()

    mission_file = 'mission_square.yaml'
    if len(sys.argv) > 1:
        mission_file = sys.argv[1]

    send_future = node.send_goal(mission_file)
    rclpy.spin_until_future_complete(node, send_future)
    goal_handle = send_future.result()

    if not goal_handle.accepted:
        node.get_logger().error('Goal was rejected by server.')
        return

    result_future = goal_handle.get_result_async()

    try:
        rclpy.spin_until_future_complete(node, result_future)
        res = result_future.result().result
        node.get_logger().info(
            f'Mission Completed! Success: {res.success} | Waypoints: {res.waypoints_completed} | Distance: {res.total_distance:.2f}m'
        )
    except KeyboardInterrupt:
        node.get_logger().info('Ctrl+C detected! Canceling goal...')
        cancel_future = goal_handle.cancel_goal_async()
        rclpy.spin_until_future_complete(node, cancel_future)
        node.get_logger().info('Goal cancel complete.')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

