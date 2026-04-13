#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool
import serial
import random
import threading
import time

class AudioNode(Node):
    def __init__(self):
        super().__init__('audio_node')

        self.ser = serial.Serial('COM3', 115200, timeout=10)
        self.is_playing = False
        self.lock = threading.Lock()
        self.current_state = None

        self.get_logger().info('Audio node started')

        self.create_subscription(Bool, 'recognized_face',   self.recognized_face_cb,   10)
        self.create_subscription(Bool, 'unrecognized_face', self.unrecognized_face_cb, 10)
        self.create_subscription(Bool, 'multiple_faces',    self.multiple_faces_cb,    10)
        self.create_subscription(Bool, 'leaving',           self.leaving_cb,           10)
        self.create_subscription(Bool, 'empty',             self.empty_cb,             10)

    def play_track(self, track_num, state_name):
        with self.lock:
            if self.is_playing:
                self.get_logger().info('Already playing, skipping trigger')
                return
            self.is_playing = True
            self.current_state = state_name

        # Run in background thread so ROS spin loop is never blocked
        t = threading.Thread(target=self._play_and_wait, args=(track_num,), daemon=True)
        t.start()

    def _play_and_wait(self, track_num):
        try:
            self.ser.write(f'PLAY:{track_num}\n'.encode())
            self.get_logger().info(f'Playing track {track_num}')

            while True:
                line = self.ser.readline().decode('utf-8', errors='ignore').strip()
                if line.startswith('DURATION:'):
                    duration = int(line.split(':')[1])
                    self.get_logger().info(f'Track duration: {duration}s')
                    time.sleep(duration + 1)
                    break
                elif line:
                    self.get_logger().info(f'Arduino: {line}')
        except Exception as e:
            self.get_logger().error(f'Playback error: {e}')
        finally:
            with self.lock:
                self.is_playing = False

    def recognized_face_cb(self, msg):
        if msg.data and self.current_state != 'recognized_face':
            self.play_track(random.randint(1, 4), 'recognized_face')

    def unrecognized_face_cb(self, msg):
        if msg.data and self.current_state != 'unrecognized_face':
            self.play_track(random.randint(5, 8), 'unrecognized_face')

    def multiple_faces_cb(self, msg):
        if msg.data and self.current_state != 'multiple_faces':
            self.play_track(random.randint(9, 10), 'multiple_faces')

    def leaving_cb(self, msg):
        if msg.data and self.current_state != 'leaving':
            self.play_track(random.randint(11, 12), 'leaving')

    def empty_cb(self, msg):
        if msg.data and self.current_state != 'empty':
            self.play_track(random.randint(13, 14), 'empty')

    def destroy_node(self):
        self.ser.close()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = AudioNode()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
