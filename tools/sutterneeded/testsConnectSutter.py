import unittest
import sutterdevice as sd
import communication.serialport as s_ports


class TestConnectSutter(unittest.TestCase):
    def testConnectDebugSutter(self):
        sutter = sd.SutterDevice("debug")
        self.assertIsNotNone(sutter.port)
        position = sutter.position()
        print(position)
        self.assertIsNotNone(position[0])
        self.assertIsNotNone(position[1])
        self.assertIsNotNone(position[2])

    def testMoveToDebugSutter(self):
        sutter = sd.SutterDevice("debug")
        self.assertIsNotNone(sutter.port)
        sutter.moveTo((0, 100, 4000))
        position = sutter.position()
        self.assertTrue(position[0] == 0)
        self.assertTrue(position[1] == 100)
        self.assertTrue(position[2] == 4000)

    def testListStageDevices(self):
        ports = s_ports.SerialPort.matchPorts(idVendor=4930, idProduct=1)
        self.assertIsInstance(ports, list)
        self.assertTrue(ports)
        print(ports)
        # then we would try to match the port using the selected index. There is no function for that yet
