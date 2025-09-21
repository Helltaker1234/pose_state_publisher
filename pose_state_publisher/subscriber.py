import rclpy
from rclpy.node import Node

# 메시지 타입 불러오기
from pose_state_publisher_interfaces.msg import PoseInfo
from geometry_msgs.msg import Twist



# 화면 기준 값
RIGHT_X_MAX = 255 
LEFT_X_MAX = -255

# twist p 제어기 게인
KP_ANGULAR_VEL = 0.01
KP_LINEAR_VEL = 0.1

# 바퀴 간격
WHEEL_DISTANCE = 0.297
WHEEL_RADIUS = 0.033

# 최대 twist 속도 제한
MAX_X_LINEAR_VEL = 0.05 # m/s
MAX_Z_ANGULAR_VEL = 0.17 # m/s

# Twist 제어기 reference value
REF_LINEAR = 0.50 # THRESH_AREA_NEAR
REF_ANGULAR = 0.0

# Twist publish 주기
TWIST_PUBLISH_PERIOD = 0.5 


class PoseStateSubscriber(Node):

    def __init__(self):
        super().__init__('pose_state_subscriber')

        # 사진의 객체 위치를 구독하는 노드 생성 
        self.subscription = self.create_subscription(
            PoseInfo,
            'pose_info',
            self.listener_callback,
            10)
        self.subscription # prevent unused variable warning
        self.get_logger().info('(Pose) Subscriber node is ready. Waiting for messages...')

        # 객체의 위치를 바탕으로 나아가야 하는 차량의 Twist 속도값 발행 노드 생성
        self.publisher = self.create_publisher(
            Twist,
            '/cmd_vel_tracker',
            10
        )
        self.get_logger().info('(Twist) Publisher node is ready. Waiting for messages...')

        self.pub_msg = Twist() # 발행할 메시지 변수 선언

        timer_period = TWIST_PUBLISH_PERIOD 
        self.timer = self.create_timer(timer_period, self.twist_pub)



    def listener_callback(self, msg):
        # 메시지의 state 값을 확인

        # if msg.state == 'HANDUP_DETECT':

        if msg.state == 'APPROACHING':
            self.get_logger().info('-----------------------------------------')
            self.get_logger().info('>> APPROACHING: Printing message <<')
            self.get_logger().info(f'Ratio: {msg.ratio}')
            self.get_logger().info(f'X_offset: {msg.x_offset}')

            self.cal_twist(msg.x_offset, msg.ratio)
        
            self.get_logger().info(f'vel_angular_z: {self.pub_msg.angular.z}')
            self.get_logger().info(f'vel_linear_x: {self.pub_msg.linear.x}')

            self.get_logger().info('-----------------------------------------')


        elif msg.state == 'ARRIVE':
            self.get_logger().info('>> ARRIVE: Shutting down node... <<')

            # 노드종료
            rclpy.shutdown()

        else:
            self.get_logger().info(f'Received message, but state is: {msg.state}')

    def cal_twist(self, measured_angle, measured_distance):

        vel_angular_z = (REF_ANGULAR - measured_angle) * KP_ANGULAR_VEL
        vel_linear_x = (REF_LINEAR - measured_distance) * KP_LINEAR_VEL

        # 최대 속도 제한
        # 매우 중요 !!!!!!!!!!!!!!!!!!!!!!1
        if(vel_linear_x > MAX_X_LINEAR_VEL): 
            vel_linear_x = MAX_X_LINEAR_VEL
        elif(vel_linear_x < 0 ):
            vel_linear_x = -vel_linear_x
        else:
            vel_linear_x = vel_linear_x

        if(abs(vel_angular_z) > MAX_Z_ANGULAR_VEL): 
            if(vel_angular_z < 0):
                vel_angular_z = -MAX_Z_ANGULAR_VEL
            else:
                vel_angular_z = MAX_Z_ANGULAR_VEL
        else:
            if(vel_angular_z < 0):
                vel_angular_z = -vel_angular_z
            else:
                vel_angular_z = vel_angular_z

        self.pub_msg.linear.x = vel_linear_x
        self.pub_msg.angular.z = vel_angular_z

    def twist_pub(self): self.publisher.publish(self.pub_msg)


def main(args=None):
    rclpy.init(args=args)

    pose_state_subscriber = PoseStateSubscriber()
    rclpy.spin(pose_state_subscriber)

    pose_state_subscriber.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()