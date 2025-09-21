import rclpy as rp
from rclpy.node import Node

from geometry_msgs.msg import Twist

class TurtlesimPublisher(Node):

    def __init__(self):
        super.__init__('turtlesim_publisher')

        self.publisher = self.create_publisher(
            Twist,
            '/diffbot_base_controller/cmd_vel_unstamped',
            10
        )
        # 1번째 매개변수는 발행할 메시지를 선택한다.
        # 2번째 매개변수는 발행할 토픽을 선택한다.
        # 4번째 매개변수는 발행자 버퍼의 크기를 지정한다.
        #
        # 2번째 매개변수 토픽의 메시지 타입은 1번째 매개변수여야 한다.
        # 
        # 발행자 버퍼:
        # 발행자는 메시지를 네트워크로 전송하기 전에 내부적으로 지정된 크기만큼 메시지를 버퍼에 저장합니다. 
        # 이 버퍼는 발행자가 메시지를 빠르게 생성하지만 네트워크 전송이 느릴 때, 메시지 유실을 방지하기 위해 존재합니다.
        #
        # 구독자 버퍼:
        # 구독자는 네트워크로부터 전달받은 메시지를 자체적으로 버퍼에 저장합니다. 
        # 구독자가 메시지를 즉시 처리하지 못할 경우, 이 버퍼에 저장된 메시지 중 최신 N개(depth만큼)만 보관하고, 나머지는 삭제됩니다.


        timer_period = 0.5
        self.timer = self.create_timer(timer_period, self.timer_callback)
        # timer_period [sec] 마다 timer_callback 호출

    def timer_callback(self):
        msg = Twist()
        msg.linear.x = 2.0
        msg.angular.z = 2.0

        self.publisher.publish(msg)
        # 생성된 구독자가 토픽을 통해 메시지를 발행함.

def main(args=None):
    rp.init(args=args)

    turtlesim_publisher = TurtlesimPublisher()
    rp.spin(turtlesim_publisher)

    turtlesim_publisher.destroy_node()
    rp.shutdown()


if __name__ == '__main__':
    main()
