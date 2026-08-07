import rclpy
import serial
import time
from rclpy.node import Node
from std_msgs.msg import Float32
from sensor_msgs.msg import JointState
from robot_interfaces.msg import STargetedFloat

class QtpyScienceNode(Node):

    def __init__(self):
        super().__init__('qtpy_science_node')

        # --------------------------------------
        # PARAMETERS
        # --------------------------------------
        self.declare_parameter('qtpy_path', '/dev/urc/mc/qtpy')
        self.qtpy_path = self.get_parameter('qtpy_path').value

        # --------------------------------------
        # SERIAL CONNECTION
        # --------------------------------------
        self.start_qtpy_connection_blocking()

        # --------------------------------------
        # PUBLISHERS
        # --------------------------------------
        self.moisture_pub = self.create_publisher(Float32, 'manipulator_moisture', 10)
        self.temp_pub = self.create_publisher(Float32, 'manipulator_temp', 10)
        self.actuator_pub = self.create_publisher(STargetedFloat, '/science/actuator_pos', 10)
        self.force_pub = self.create_publisher(Float32, 'manipulator_force', 10)  # NEW

        # --------------------------------------
        # SUBSCRIBERS
        # --------------------------------------
        self.actuator_sub = self.create_subscription(
            STargetedFloat,
            '/science/actuator_pos',
            self.actuator_callback,
            10
        )

        self.joint_vel_sub = self.create_subscription(
            JointState,
            'joint_vel',
            self.joint_vel_callback,
            10
        )

        # --------------------------------------
        # STREAM TIMER
        # --------------------------------------
        self.create_timer(0.05, self.read_stream)

    # =======================================
    # JOINT VEL BRIDGE
    # =======================================
    def joint_vel_callback(self, msg: JointState):
        try:
            idx = msg.name.index("finger")
        except ValueError:
            self.get_logger().warn("'finger' joint not found in joint_vel message")
            return

        val = msg.velocity[idx]

        if val not in (0.0, 0.5, 1.0):
            self.get_logger().warn(f"Unexpected finger value: {val}, ignoring")
            return

        out = STargetedFloat()
        out.target = 'act'
        out.data = float(val)
        self.actuator_pub.publish(out)

    # =======================================
    # SERIAL CONNECT
    # =======================================
    def start_qtpy_connection_blocking(self):
        while True:
            try:
                self.get_logger().info("Connecting to QT Py...")
                self.port = serial.Serial(
                    port=self.qtpy_path,
                    baudrate=115200,
                    timeout=0.1
                )
                self.get_logger().info("QT Py connected.")
                time.sleep(2)
                return
            except serial.SerialException:
                self.get_logger().warn("QT Py not found, retrying...")
                time.sleep(1)

    # =======================================
    # ACTUATOR COMMAND CALLBACK
    # =======================================
    def actuator_callback(self, msg: STargetedFloat):
        try:
            if msg.target != 'act':
                return

            if msg.data == 1.0:
                cmd = "extend\n"
            elif msg.data == 0.0:
                cmd = "retract\n"
            elif msg.data == 0.5:
                cmd = "stop\n"
            else:
                return

            self.port.write(cmd.encode())
            self.get_logger().info(f"Sent command: {cmd.strip()}")

        except Exception as e:
            self.get_logger().error(f"Actuator write error: {e}")

    # =======================================
    # SERIAL STREAM READER
    # =======================================
    def read_stream(self):
        try:
            line = self.port.readline().decode(errors='ignore').strip()

            if not line:
                return

            parts = line.split(",")

            # Force sensor data
            if parts[0].lower().startswith("force") and len(parts[0].split()) == 2:
                try:
                    force_val = float(parts[0].split()[1])
                    self.force_pub.publish(Float32(data=force_val))
                except ValueError:
                    pass
                return

            # Moisture/temp data
            if len(parts) != 2:
                return

            try:
                moisture = float(parts[0])
                temp = float(parts[1])
            except ValueError:
                return

            self.moisture_pub.publish(Float32(data=moisture))
            self.temp_pub.publish(Float32(data=temp))

        except serial.SerialException:
            self.get_logger().error("Serial disconnected. Reconnecting...")
            self.start_qtpy_connection_blocking()


def main(args=None):
    rclpy.init(args=args)
    node = QtpyScienceNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()