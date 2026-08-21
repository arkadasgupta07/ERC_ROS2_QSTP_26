import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from std_srvs.srv import SetBool


class ObstacleAvoiderNode(Node):

    def __init__(self):
        super().__init__('obstacle_avoider')

        self.is_active = False
        self.angular_speed = 0.5

        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.scan_sub = self.create_subscription(
            LaserScan, '/scan', self.scan_callback, 10
        )
        self.srv = self.create_service(
            SetBool, '/toggle_robot', self.toggle_robot_callback
        )

        self.get_logger().info('Obstacle Avoider Node Ready (State: OFF)')

    def toggle_robot_callback(self, request, response):
        self.is_active = request.data
        if self.is_active:
            self.angular_speed = 0.5
            response.success = True
            response.message = 'Robot state set to ON.'
            self.get_logger().info('Robot turned ON')
        else:
            stop_msg = Twist()
            self.cmd_pub.publish(stop_msg)
            response.success = True
            response.message = 'Robot state set to OFF.'
            self.get_logger().info('Robot turned OFF')
        return response

    def scan_callback(self, msg):
        cmd = Twist()

        if not self.is_active:
            self.cmd_pub.publish(cmd)
            return

        ranges = msg.ranges
        num_ranges = len(ranges)
        if num_ranges == 0:
            return

        front_indices = list(range(0, 15)) + list(
            range(num_ranges - 15, num_ranges)
        )
        front_ranges = [
            ranges[i]
            for i in front_indices
            if not math.isnan(ranges[i])
            and not math.isinf(ranges[i])
            and ranges[i] > 0
        ]

        min_front_dist = min(front_ranges) if front_ranges else 10.0

        left_idx = int(num_ranges * 90 / 360)
        right_idx = int(num_ranges * 270 / 360)

        left_dist = (
            ranges[left_idx]
            if not math.isnan(ranges[left_idx])
            and not math.isinf(ranges[left_idx])
            else 0.0
        )
        right_dist = (
            ranges[right_idx]
            if not math.isnan(ranges[right_idx])
            and not math.isinf(ranges[right_idx])
            else 0.0
        )

        if min_front_dist < 0.7:
            cmd.linear.x = 0.05
            cmd.angular.z = 0.6 if left_dist > right_dist else -0.6
            self.angular_speed = 0.5
        else:
            cmd.linear.x = 0.2
            cmd.angular.z = self.angular_speed
            self.angular_speed = max(0.08, self.angular_speed - 0.001)

        self.cmd_pub.publish(cmd)


def main(args=None):
    rclpy.init(args=args)
    node = ObstacleAvoiderNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()