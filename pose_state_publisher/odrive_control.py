import rclpy
from rclpy.node import Node
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


class ODRIVE_CONTROL():

    def __init__(self):

        self.vel_angular_z = 0
        self.vel_linear_x = 0
        self.right_wheel_vel = 0
        self.left_wheel_vel = 0

    def odrive_init(self):

        # ODrive 설정
        self.get_logger().info("Finding ODrive...")
        try:
            self.odrv0 = odrive.find_any()
            self.get_logger().info("ODrive found.")
        except Exception as e:
            self.get_logger().error(f"Failed to find ODrive: {e}")
            rclpy.shutdown()
            return
        
        # 파라미터 선언 및 초기화
        self.declare_parameter('wheel_diameter', 0.0702)
        self.declare_parameter('wheel_separation', 0.465)
        self.wheel_diameter = self.get_parameter('wheel_diameter').get_parameter_value().double_value
        self.wheel_separation = self.get_parameter('wheel_separation').get_parameter_value().double_value

        # 제어 루프 및 상태 설정
        self.odrv0.axis0.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
        self.odrv0.axis1.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
        self.odrv0.axis0.controller.config.control_mode = CONTROL_MODE_VELOCITY_CONTROL
        self.odrv0.axis1.controller.config.control_mode = CONTROL_MODE_VELOCITY_CONTROL
        self.odrv0.axis0.controller.input_vel = 0.0
        self.odrv0.axis1.controller.input_vel = 0.0

        self.get_logger().info("ODrive Control Node has started.")

        self.is_enabled = True


    def odrive_drive_wheel(self, ref_angle, ref_distance):

        vel_angular_z = ref_angle * KP_ANGULAR_VEL
        vel_linear_x = ref_distance * KP_LINEAR_VEL

        # 최대 속도 제한
        # 매우 중요 !!!!!!!!!!!!!!!!!!!!!!1
        if(vel_linear_x > MAX_X_LINEAR_VEL): vel_linear_x = MAX_X_LINEAR_VEL
        if(vel_angular_z > MAX_Z_ANGULAR_VEL): vel_angular_z = MAX_Z_ANGULAR_VEL

        right_wheel_vel = (vel_linear_x + WHEEL_DISTANCE * vel_angular_z / 2) / WHEEL_RADIUS
        left_wheel_vel = (vel_linear_x - WHEEL_DISTANCE * vel_angular_z / 2)
    
        self.odrv0.axis0.controller.input_vel = right_wheel_vel
        self.odrv0.axis1.controller.input_vel = left_wheel_vel


    def odrive_shutdown(self):
        self.odrv0.axis0.controller.input_vel = 0.0
        self.odrv0.axis1.controller.input_vel = 0.0

        self.odrv0.axis0.requested_state = AXIS_STATE_IDLE
        self.odrv0.axis1.requested_state = AXIS_STATE_IDLE