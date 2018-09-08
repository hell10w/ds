import unittest

from ds.somemodule import MyClass


class TestMyClass(unittest.TestCase):
    def test_x(self):
        instance = MyClass()
        self.assertEqual(instance.x, 1)

    def test_y(self):
        instance = MyClass()
        self.assertEqual(instance.y, 2)

    def test_z(self):
        instance = MyClass()
        self.assertEqual(instance.z, 3)
