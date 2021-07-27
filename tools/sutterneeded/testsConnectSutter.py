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

    def testMoveToWithDebugSutter(self):
        sutter = sd.SutterDevice("debug")
        self.assertIsNotNone(sutter.port)
        sutter.moveTo((0, 100, 4000))
        position = sutter.position()
        self.assertTrue(position[0] == 0)
        self.assertTrue(position[1] == 100)
        self.assertTrue(position[2] == 4000)

    def testListStageDevices(self):
        sp = s_ports.SerialPort()
        ports = sp.matchPorts(idVendor=4930, idProduct=1)
        self.assertIsInstance(ports, list)
        self.assertTrue(ports)
        print(ports)
        # then we would try to match a port using the selected index. There is no function for that yet.
        sp.portPath = ports[0]
        sp.open()
        self.assertIsNotNone(sp.port)  # self.assertTrue(sp.isOpen())
