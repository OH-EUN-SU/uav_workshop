from djitellopy import Tello
import time

tello = Tello()
tello.connect()

print(tello.get_battery())

distance = 60
angle = 90

tello.takeoff()
time.sleep(1)

for i in range(4):
    tello.rotate_counter_clockwise(angle)
    time.sleep(1)
    tello.move_forward(distance)
    time.sleep(1)

tello.land()