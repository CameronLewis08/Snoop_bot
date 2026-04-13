#!/usr/bin/env python3
import json
import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool


class FaceStateNode(Node):
    def __init__(self):
        super().__init__('face_state_node')

        self.previous_names = []

        self.create_subscription(String, '/face_recognition/data', self.face_data_cb, 10)

        self.pub_recognized   = self.create_publisher(Bool, 'recognized_face',   10)
        self.pub_unrecognized = self.create_publisher(Bool, 'unrecognized_face', 10)
        self.pub_multiple     = self.create_publisher(Bool, 'multiple_faces',    10)
        self.pub_leaving      = self.create_publisher(Bool, 'leaving',           10)
        self.pub_empty        = self.create_publisher(Bool, 'empty',             10)

    def face_data_cb(self, msg):
        data = json.loads(msg.data)
        current_names = data['names']
        previous_names = self.previous_names
        prev_count = len(previous_names)
        curr_count = len(current_names)

        self.get_logger().info(f'Received: {current_names} (previous: {previous_names})')

        # multiple → single or empty: someone left the group
        if prev_count > 1 and curr_count < prev_count:
            self.get_logger().info('State: leaving')
            self._publish(self.pub_leaving)
        # non-empty → empty: last person left
        elif prev_count > 0 and curr_count == 0:
            self.get_logger().info('State: leaving')
            self._publish(self.pub_leaving)
        # no faces
        elif curr_count == 0:
            self.get_logger().info('State: empty')
            self._publish(self.pub_empty)
        # multiple faces visible
        elif curr_count > 1:
            self.get_logger().info('State: multiple_faces')
            self._publish(self.pub_multiple)
        # single recognized person
        elif current_names[0] != 'Unknown':
            self.get_logger().info('State: recognized_face')
            self._publish(self.pub_recognized)
        # single unrecognized person
        else:
            self.get_logger().info('State: unrecognized_face')
            self._publish(self.pub_unrecognized)

        self.previous_names = current_names

    def _publish(self, publisher):
        msg = Bool()
        msg.data = True
        publisher.publish(msg)
        self.get_logger().info(f'Published Bool True to {publisher.topic_name}')


def main(args=None):
    rclpy.init(args=args)
    node = FaceStateNode()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == '__main__':
    main()
