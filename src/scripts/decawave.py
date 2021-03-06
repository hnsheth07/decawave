#!/usr/bin/env python
import rospy
import serial
import time
from std_msgs.msg import String
from sensor_msgs.msg import Range
import pdb
from collections import deque


def distance_measurement():
    pub = rospy.Publisher('range', Range, queue_size=10)
    rospy.init_node('decawave', anonymous=True)
    rate = rospy.Rate(10)
    while not rospy.is_shutdown():
        ser = serial.Serial(
            port='/dev/ttyACM0',
            baudrate=115200,
            timeout=0.1
        )

        ser.write(b'\r\r')
        res=ser.read(100000)
        time.sleep(1)
        ser.write(b'lec\r')
        print(res)

        q = deque()
        total = 0
        while True:
            res=ser.read(100)
            distance = Range()

            if len(res)>0:
                readings = res.split('\r\n')
                for reading in readings:
                    if 'DIST' in reading:
                        try:
                            range_deca = float(reading.split(',')[-1])
                            if range_deca:
                                q.append(range_deca)
                                if len(q) <= 10:
                                    total += range_deca
                                else:
                                    removed_element = q.popleft()
                                    print(q)
                                    total = total - removed_element + range_deca
                                    distance.range = total/len(q)
                                    distance.header.stamp = rospy.get_rostime()
                                    rospy.loginfo(distance)
                                    pub.publish(distance)
                        except ValueError as e:
                            rospy.loginfo("A string found")

if __name__ == "__main__":
    try:
        distance_measurement()
    except rospy.ROSInterruptException:
        pass
