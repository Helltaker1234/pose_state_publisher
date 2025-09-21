import rclpy
from rclpy.node import Node

# from odrive_control import ODRIVE_CONTROL


# 메시지 타입 불러오기
from pose_state_publisher_interfaces.msg import PoseInfo

from std_msgs.msg import Float64MultiArray
from sensor_msgs.msg import JointState
import odrive
from odrive.enums import *
import math
import os
import time



# 화면 기준 값
RIGHT_X_MAX = 255 
LEFT_X_MAX = -255

# twist p 제어기 게인
KP_ANGULAR_VEL = 100
KP_LINEAR_VEL = 100

# 바퀴 간격
WHEEL_DISTANCE = 0.297
WHEEL_RADIUS = 0.033

# 최대 twist 속도 제한
MAX_X_LINEAR_VEL = 0.08 # m/s
MAX_Z_ANGULAR_VEL = 0.17 # m/s



class PoseStateSubscriber(Node):

    odrv0 = odrive.find_any()

    def __init__(self):
        super().__init__('pose_state_subscriber')
        self.subscription = self.create_subscription(
            PoseInfo,
            'pose_info',
            self.listener_callback,
            10)
        self.subscription # prevent unused variable warning
        self.get_logger().info('Subscriber node is ready. Waiting for messages...')

        # ODrive 설정
        # self.get_logger().info("Finding ODrive...")
        # try:
        #     self.odrv0 = odrive.find_any()
        #     self.get_logger().info("ODrive found.")
        # except Exception as e:
        #     self.get_logger().error(f"Failed to find ODrive: {e}")
        #     rclpy.shutdown()
        #     return

        # 제어 루프 및 상태 설정
        self.odrv0.axis0.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
        self.odrv0.axis1.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
        self.odrv0.axis0.controller.config.control_mode = CONTROL_MODE_VELOCITY_CONTROL
        self.odrv0.axis1.controller.config.control_mode = CONTROL_MODE_VELOCITY_CONTROL
        self.odrv0.axis0.controller.input_vel = 0.0
        self.odrv0.axis1.controller.input_vel = 0.0

        self.get_logger().info("ODrive Control Node has started.")


    def listener_callback(self, msg):
        # 메시지의 state 값을 확인

        # if msg.state == 'HANDUP_DETECT':

        if msg.state == 'APPROACHING':
            self.get_logger().info('-----------------------------------------')
            self.get_logger().info('>> APPROACHING: Printing message <<')
            self.get_logger().info(f'Ratio: {msg.ratio}')
            self.get_logger().info(f'X_offset: {msg.x_offset}')
            self.get_logger().info('-----------------------------------------')

            self.odrive_drive_wheel(msg.x_offset, msg.ratio)

            
        
        elif msg.state == 'ARRIVE':
            self.get_logger().info('>> ARRIVE: Shutting down node... <<')
            self.odrv_cont.odrive_shutdown()

            # 노드종료
            rclpy.shutdown()

        else:
            self.get_logger().info(f'Received message, but state is: {msg.state}')

    
    def odrive_drive_wheel(self, ref_angle, ref_distance):

        vel_angular_z = ref_angle * KP_ANGULAR_VEL
        vel_linear_x = ref_distance * KP_LINEAR_VEL

        # 최대 속도 제한
        # 매우 중요 !!!!!!!!!!!!!!!!!!!!!!1
        if(vel_linear_x > MAX_X_LINEAR_VEL): vel_linear_x = MAX_X_LINEAR_VEL
        if(vel_angular_z > MAX_Z_ANGULAR_VEL): vel_angular_z = MAX_Z_ANGULAR_VEL

        right_wheel_vel = (vel_linear_x + WHEEL_DISTANCE * vel_angular_z / 2) / WHEEL_RADIUS
        left_wheel_vel = (vel_linear_x - WHEEL_DISTANCE * vel_angular_z / 2) / WHEEL_RADIUS
    
        self.odrv0.axis0.controller.input_vel = right_wheel_vel
        self.odrv0.axis1.controller.input_vel = left_wheel_vel


def main(args=None):
    rclpy.init(args=args)
    pose_state_subscriber = PoseStateSubscriber()
    rclpy.spin(pose_state_subscriber)
    pose_state_subscriber.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()