import rclpy
import serial
import time
from rclpy.node import Node
from std_msgs.msg import Float32, Bool
from robot_interfaces.msg import STargetedFloat
from robot_interfaces.msg import STargetedBool

### Linear Actuator Commands: ###
#extend
#ros2 topic pub --once /science/actuator_pos robot_interfaces/msg/STargetedFloat "{target: 'act', data: 1.0}"

#retract
#ros2 topic pub --once /science/actuator_pos robot_interfaces/msg/STargetedFloat "{target: 'act', data: 0.0}"

#stop
#ros2 topic pub --once /science/actuator_pos robot_interfaces/msg/STargetedFloat "{target: 'act', data: 0.5}"

class PicoWriter(Node):

    def __init__(self):
        super().__init__('pico_science_node')

        # --------------------------------------
        # PARAMETERS
        # --------------------------------------
        self.declare_parameter('pico_path', '/dev/urc/mc/pi_pico')
        self.pico_path = self.get_parameter('pico_path').value

        self.bl = False

        # --------------------------------------
        # SERIAL CONNECTION
        # --------------------------------------
        self.start_pico_connection_blocking()

        # --------------------------------------
        # SUBSCRIBERS
        # --------------------------------------
        self.create_subscription(
            STargetedFloat,
            '/science/actuator_pos',
            self.send_to_pico_act,
            10
        )

        self.create_subscription(
            STargetedBool,
            '/relay_status',
            self.send_to_pico_relay,
            10
        )

        # --------------------------------------
        # PUBLISHERS
        # --------------------------------------
        self.temp1_pub = self.create_publisher(Float32, 'temp1', 10)
        self.press1_pub = self.create_publisher(Float32, 'pressure1', 10)
        self.hum1_pub = self.create_publisher(Float32, 'humidity1', 10)

        self.temp2_pub = self.create_publisher(Float32, 'temp2', 10)
        self.press2_pub = self.create_publisher(Float32, 'pressure2', 10)
        self.hum2_pub = self.create_publisher(Float32, 'humidity2', 10)

        self.limit_switch_1_pub = self.create_publisher(Bool, '/limit_switch_1', 10)
        self.limit_switch_2_pub = self.create_publisher(Bool, '/limit_switch_2', 10)
        self.limit_switch_1_state = 0 #Not Triggered, 1 if Triggered
        self.limit_switch_2_state = 0

        # --------------------------------------
        # STREAM TIMER
        # --------------------------------------
        self.create_timer(0.2, self.read_stream)

    # =======================================
    # SERIAL CONNECT
    # =======================================
    def start_pico_connection_blocking(self):
        while True:
            try:
                self.get_logger().info("Connecting to Pico...")
                self.port = serial.Serial(
                    port=self.pico_path,
                    baudrate=115200,
                    timeout=0.5
                )
                self.get_logger().info("Pico connected.")
                return
            except serial.SerialException:
                time.sleep(1)

    # =======================================
    # STREAM READER
    # =======================================
    def read_stream(self):
        try:
            line = self.port.readline().decode(errors='ignore').strip()
            self.get_logger().debug(f"Received line: '{line}'")
            if not line:
                self.get_logger().debug("No data received from Pico.")
                return

            parts = line.split(",")

            # Ignore malformed lines or boot messages ##change back to 6 after test
            if len(parts) != 8:
                self.get_logger().debug(f"Received malformed line: '{line}'")
                return

            try:
                t1 = float(parts[0])
                p1 = float(parts[1])
                h1 = float(parts[2])
                t2 = float(parts[3])
                p2 = float(parts[4])
                h2 = float(parts[5])
                lim1 = float(parts[6])
                lim2 = float(parts[7])
            except ValueError:
                self.get_logger().debug(f"Received non-numeric data: '{line}'")
                return

            # Sensor 1
            self.temp1_pub.publish(Float32(data=t1))
            self.press1_pub.publish(Float32(data=p1))
            self.hum1_pub.publish(Float32(data=h1))

            # Sensor 2
            self.temp2_pub.publish(Float32(data=t2))
            self.press2_pub.publish(Float32(data=p2))
            self.hum2_pub.publish(Float32(data=h2))

            self.limit_switch_1_pub.publish(Bool(data=bool(lim1)))
            self.limit_switch_2_pub.publish(Bool(data=bool(lim2)))

        except serial.SerialException:
            self.start_pico_connection_blocking()

    # =======================================
    # ACTUATOR COMMAND (DISCRETE)
    # =======================================
    def send_to_pico_act(self, msg):
        try:
            if msg.target != "act":
                return

            if msg.data == 1.0:
                cmd = "act_extend\n"
            elif msg.data == 0.0:
                cmd = "act_retract\n"
            elif msg.data == 0.5:
                cmd = "act_stop\n"
            else:
                return  # ignore unexpected values

            self.port.write(cmd.encode())
            self.get_logger().info(f"Sent command: {cmd.strip()}")

        except serial.SerialException:
            self.start_pico_connection_blocking()

    # =======================================
    # RELAY COMMAND
    # =======================================
    def send_to_pico_relay(self, msg):
        try:
            if msg.target == "hb":
                self.port.write(("hbon\n" if msg.data else "hboff\n").encode())

            elif msg.target == "vib":
                self.port.write(("vibon\n" if msg.data else "viboff\n").encode())

        except serial.SerialException:
            self.start_pico_connection_blocking()


def main(args=None):
    rclpy.init(args=args)
    node = PicoWriter()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
