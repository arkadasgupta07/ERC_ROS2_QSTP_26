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

    ''' 2. Service Switch (toggle_robot_callback) '''
    '''
    Toggles self.is_active based on incoming service request (request.data).
    If set to False, it immediately publishes an empty Twist() message to halt motor movement safely.
    '''
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

    ''' 3. LiDAR Processing and Control Logic (scan_callback) '''
    '''
    scan_callback acts as the robot's real-time control loop it runs automatically every single time the LiDAR fires a scan (around 5 to 10 times per second).
    '''
    
    def scan_callback(self, msg):
        
        
        
        cmd = Twist()

        if not self.is_active:
            self.cmd_pub.publish(cmd)
            return

        ''' 
                cmd = Twist(): Initializes a blank velocity message where all linear and angular speeds default to 0.0 (stop state).
                if not self.is_active: Checks your state switch. If the service hasn't set self.is_active = True, it publishes zero speed to keep the robot motionless and exits (return) immediately to save CPU cycles.
                '''


        ranges = msg.ranges
        num_ranges = len(ranges)
        if num_ranges == 0:
            return
        '''
        msg.ranges: An array containing distance measurements in meters.
        Each spot in the array corresponds to a specific angle around the robot
        ($0^\circ$ is directly ahead, $90^\circ$ is left, $180^\circ$ is behind, and $270^\circ$ is right).
        '''
        

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
        ''' Dynamically converts $90^\circ$ (left) and $270^\circ$ (right) into array index positions, keeping the node compatible with any LiDAR sensor resolution. '''

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



        '''
        Executes control decision tree:-
        Obstacle Flanking: If front obstacle $< 0.7\text{m}$, slows forward movement and steers toward whichever side has more clearance (+0.6 rad/s left, -0.6 rad/s right). Resets spiral radius variable.
        Spiraling: If path is clear, drives forward at $0.2\text{ m/s}$ while linearly decrementing turning speed (self.angular_speed) down to a lower bound of $0.08\text{ rad/s}$.
        '''
        
        if min_front_dist < 0.7:
            cmd.linear.x = 0.05
            cmd.angular.z = 0.6 if left_dist > right_dist else -0.6
            self.angular_speed = 0.5
        else:
            cmd.linear.x = 0.2
            cmd.angular.z = self.angular_speed
            self.angular_speed = max(0.08, self.angular_speed - 0.001)
            
        ''' 
        Obstacle Flanking Condition (< 0.7m):-
        Slows down forward movement (0.05 m/s).
        Compares space: if left_dist > right_dist, it turns left (+0.6 rad/s); otherwise, it turns right (-0.6 rad/s).
        Resets self.angular_speed = 0.5 so a fresh spiral starts once clear.

        Clear Path Spiral Condition (>= 0.7m):
        Moves forward at constant speed (0.2 m/s).
        Decrements turning rate slightly on every loop (self.angular_speed - 0.001).
        '''

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