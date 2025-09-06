import rclpy
from rclpy.node import Node

from odrive_control import ODRIVE_CONTROL


# 메시지 타입 불러오기
from pose_state_publisher_interfaces.msg import PoseInfo

class PoseStateSubscriber(Node):

    def __init__(self):
        super().__init__('pose_state_subscriber')
        self.subscription = self.create_subscription(
            PoseInfo,
            'pose_info',
            self.listener_callback,
            10)
        self.subscription # prevent unused variable warning
        self.get_logger().info('Subscriber node is ready. Waiting for messages...')

        self.odrv_cont = ODRIVE_CONTROL()


    def listener_callback(self, msg):
        # 메시지의 state 값을 확인

        if msg.state == 'HANDUP_DETECT':
            self.odrv_cont.odrive_init()

        if msg.state == 'APPROACHING':
            self.get_logger().info('-----------------------------------------')
            self.get_logger().info('>> APPROACHING: Printing message <<')
            self.get_logger().info(f'Ratio: {msg.ratio}')
            self.get_logger().info(f'X_offset: {msg.x_offset}')
            self.get_logger().info('-----------------------------------------')

            self.odrv_cont.odrive_drive_wheel(msg.x_offset, msg.ratio)

            
        
        elif msg.state == 'ARRIVE':
            self.get_logger().info('>> ARRIVE: Shutting down node... <<')
            self.odrv_cont.odrive_shutdown()

            # 노드종료
            rclpy.shutdown()

        else:
            self.get_logger().info(f'Received message, but state is: {msg.state}')


def main(args=None):
    rclpy.init(args=args)
    pose_state_subscriber = PoseStateSubscriber()
    rclpy.spin(pose_state_subscriber)
    pose_state_subscriber.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()