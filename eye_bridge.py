import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import json
import serial
import sys

class EyeBridgeNode(Node):
    def __init__(self):
        super().__init__('eye_bridge_node')
        
        # Subscribe to the topic your partner defined
        self.subscription = self.create_subscription(
            String,
            '/face_recognition/data',
            self.listener_callback,
            10
        )

        # CHANGE THIS: Match your Nano's port (check Arduino IDE > Tools > Port)
        # Linux: '/dev/ttyACM0', Windows: 'COM3', Mac: '/dev/cu.usbmodem...'
        self.serial_port = '/dev/ttyACM0' 
        
        try:
            self.ser = serial.Serial(self.serial_port, 115200, timeout=0.1)
            self.get_logger().info(f"Connected to Nano on {self.serial_port}")
        except Exception as e:
            self.get_logger().error(f"Could not open serial port: {e}")
            sys.exit(1)

    def map_range(self, x, in_min, in_max, out_min, out_max):
        # Maps camera coordinates to screen pixel coordinates
        return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

    def listener_callback(self, msg):
        try:
            # Parse the JSON string from the ROS topic
            data = json.loads(msg.data)
            centroid = data["centroid"] # Expects [x, y]

            # Map 640x480 camera resolution to 0-240 screen range
            # We use 60-180 to keep the pupil from hitting the screen edge
            eye_x = self.map_range(centroid[0], 0, 640, 60, 180)
            eye_y = self.map_range(centroid[1], 0, 480, 90, 150)

            # Format the command for the Arduino: "X150,Y120\n"
            command = f"X{eye_x},Y{eye_y}\n"
            self.ser.write(command.encode())
            
            self.get_logger().info(f"Sent to Eyes: {command.strip()}")
            
        except Exception as e:
            self.get_logger().error(f"Error: {e}")

def main(args=None):
    rclpy.init(args=args)
    node = EyeBridgeNode()
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