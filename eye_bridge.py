import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import json
import serial
import sys

class SkeletonEyeBridge(Node):
    def __init__(self):
        super().__init__('eye_bridge_node')
        
        self.subscription = self.create_subscription(
            String,
            '/face_recognition/data',
            self.listener_callback,
            10
        )

        # Port identified via 'ls /dev/lcd' after usbipd attach
        self.serial_port = '/dev/lcd' 
        
        try:
            self.ser = serial.Serial(self.serial_port, 115200, timeout=0.1)
            self.get_logger().info(f"SUCCESS: Connected to Nano on {self.serial_port}")
        except Exception as e:
            self.get_logger().error(f"FATAL: Could not open serial port: {e}")
            self.get_logger().info("Check usbipd attach and 'sudo chmod 666 /dev/ttyACM0'")
            sys.exit(1)

    def map_range(self, x, in_min, in_max, out_min, out_max):
        # Maps camera coordinates to screen pixel coordinates
        return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

    def listener_callback(self, msg):
        try:
            data = json.loads(msg.data)
            centroid = data["centroid"] # [x, y]
            x_val = centroid[0]
            y_val = centroid[1]

            # IDLE DEADZONE: Centered at 960 (half of 1920)
            # Range: 910 to 1010 (100 pixel window)
            if 910 <= x_val <= 1010:
                command = "IDLE\n"
            else:
                # INVERTED MAPPING: 
                # Input X: 0 to 1920 -> Output X: 180 to 60
                # Input Y: 0 to 1080 -> Output Y: 90 to 150
                eye_x = self.map_range(x_val, 0, 1920, 180, 60)
                eye_y = self.map_range(y_val, 0, 1080, 90, 150)
                command = f"X{eye_x},Y{eye_y}\n"

            if self.ser and self.ser.is_open:
                self.ser.write(command.encode())
                self.get_logger().info(f"Target: {command.strip()} (Input: {x_val},{y_val})")
            
        except Exception as e:
            self.get_logger().error(f"Data Error: {e}")

def main(args=None):
    rclpy.init(args=args)
    node = SkeletonEyeBridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if node.ser:
            node.ser.close()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()