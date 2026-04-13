import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import json

class FaceDataSubscriber(Node):
    def __init__(self):
        super().__init__('face_data_subscriber')
        self.subscription = self.create_subscription(
            String,
            '/face_recognition/data',
            self.listener_callback,
            10
        )

    def listener_callback(self, msg):
        data = json.loads(msg.data)
        centroid = data["centroid"]
        names = data["names"]
        self.get_logger().info(f"Centroids: {centroid}, Name: {names}")

def main():
    rclpy.init()
    node = FaceDataSubscriber()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()