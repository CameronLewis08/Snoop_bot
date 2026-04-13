#!/usr/bin/env python3
"""
Mock publisher for testing face_state.py and rosaudio.py without a camera.
Continuously publishes the current scenario at 2Hz to simulate a live camera feed.

Usage: python3 mock_face_publisher.py
Then press a key to switch the active scenario:
  1 - recognized face (single known person)
  2 - unrecognized face (single unknown person)
  3 - multiple faces
  4 - empty (no faces)
  q - quit
"""

import json
import threading
import rclpy
from rclpy.node import Node
from std_msgs.msg import String


SCENARIOS = {
    '1': {"centroid": [960, 540], "names": ["cam"]},
    '2': {"centroid": [960, 540], "names": ["Unknown"]},
    '3': {"centroid": [960, 540], "names": ["cam", "tim"]},
    '4': {"centroid": [0, 0],    "names": []},
}

LABELS = {
    '1': 'recognized face (cam)',
    '2': 'unrecognized face (Unknown)',
    '3': 'multiple faces (cam + tim)',
    '4': 'empty',
}


class MockFacePublisher(Node):
    def __init__(self):
        super().__init__('mock_face_publisher')
        self.publisher_ = self.create_publisher(String, '/face_recognition/data', 10)
        self.current_scenario = None

        # Publish at 2Hz to simulate continuous camera frames
        self.create_timer(0.5, self.timer_callback)

    def timer_callback(self):
        if self.current_scenario is None:
            return
        msg = String()
        msg.data = json.dumps(SCENARIOS[self.current_scenario])
        self.publisher_.publish(msg)

    def set_scenario(self, key):
        self.current_scenario = key
        self.get_logger().info(f'Scenario changed to: {LABELS[key]}')


def main(args=None):
    rclpy.init(args=args)
    node = MockFacePublisher()

    # Spin in a background thread so input() can run on the main thread
    spin_thread = threading.Thread(target=rclpy.spin, args=(node,), daemon=True)
    spin_thread.start()

    print('\nMock Face Publisher ready. Publishing at 2Hz.')
    print('  1 - recognized face (cam)')
    print('  2 - unrecognized face (Unknown)')
    print('  3 - multiple faces (cam + tim)')
    print('  4 - empty')
    print('  q - quit\n')

    try:
        while True:
            key = input('Enter scenario: ').strip().lower()
            if key == 'q':
                break
            elif key in SCENARIOS:
                node.set_scenario(key)
            else:
                print('Invalid key. Use 1, 2, 3, 4, or q.')
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
