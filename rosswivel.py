#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import json
import serial
import time

class RosSwivel(Node):
    def __init__(self):
        super().__init__('ros_swivel_node')

        self.subscription = self.create_subscription(
            String,
            '/face_recognition/data',
            self.listener_callback,
            10
        )

        self.port = '/dev/ttyUSB0'
        self.ser = serial.Serial(self.port, 115200, timeout=0.1)
        self.get_logger().info(f"Connected to ESP32 on {self.port}")

        self.center = 900
        self.deadzone = 400
        self.position = 0
        self.max_position = 100

        self.last_valid_time = time.time()
        self.timeout_sec = 1.0

        self.last_command = "STOP"
        self.last_send_time = 0
        self.min_interval = 0.2

        self.pause_until = 0
        self.pause_duration = 2.0   # Pause after movement

        # Smoothing
        self.prev_x = None
        self.alpha = 0.6

    def listener_callback(self, msg):
        try:
            now = time.time()

            if now < self.pause_until:
                return

            data = json.loads(msg.data)
            x = data["centroid"][0]

            # Ignore 0
            if x == 0:
                self.check_timeout()
                return

            self.last_valid_time = now

            # Smoothing
            if self.prev_x is None:
                smoothed_x = x
            else:
                smoothed_x = self.alpha * x + (1 - self.alpha) * self.prev_x

            self.prev_x = smoothed_x

            error = smoothed_x - self.center

            self.get_logger().info(f"x={int(smoothed_x)} error={int(error)}")

            inner_deadzone = self.deadzone
            outer_deadzone = self.deadzone + 80

            if self.last_command == "STOP":
                if abs(error) < outer_deadzone:
                    self.send("STOP")
                    return
            else:
                if abs(error) < inner_deadzone:
                    self.send("STOP")
                    return

            # Limits
            if self.position >= self.max_position:
                self.send("STOP")
                return

            if self.position <= -self.max_position:
                self.send("STOP")
                return

            # Tracking
            if error > 0:
                self.send("LEFT")
                self.position += 1
                self.pause_until = now + self.pause_duration
            else:
                self.send("RIGHT")
                self.position -= 1
                self.pause_until = now + self.pause_duration

        except Exception as e:
            self.get_logger().error(f"Error: {e}")

    def check_timeout(self):
        if time.time() - self.last_valid_time > self.timeout_sec:
            self.send("STOP")

    def send(self, command):
        now = time.time()

        if command != self.last_command and (now - self.last_send_time) > self.min_interval:
            self.ser.write((command + "\n").encode())
            self.get_logger().info(f"SENT: {command}")
            self.last_command = command
            self.last_send_time = now

    def destroy_node(self):
        self.ser.write(b"STOP\n")
        time.sleep(0.1)
        self.ser.close()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = RosSwivel()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
