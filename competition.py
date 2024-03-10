from djitellopy import Tello
import time
import cv2 
import threading

DEFAULT_TELLO_SPEED = 25              
MAX_DISTANCE_BETWEEN_TWO_MPAD = 1000  
TOLERANCE_X_AXIS = 5                 
TOLERANCE_Y_AXIS = 5                 
POSITIONING_ITERATION_COUNT = 6     
MINIMUM_HEIGHT_THRESHOLD = 80     
DEFAULT_UPWARD_STEP = 20       
DEFAULT_FORWARD_STEP = 30    
DEFAULT_FORWARD_STEP_COUNT = (MAX_DISTANCE_BETWEEN_TWO_MPAD/DEFAULT_FORWARD_STEP)
DEFAULT_ROTATION_IN_DEGREE = 60    

tello = Tello()

def tello_position_near_mpad(tolerance_x, tolerance_y,mpad_id, iteration_count):
    y_min = 0-tolerance_y
    y_max = tolerance_y
    x_min = 0-tolerance_x
    x_max = tolerance_x
    loop_count = iteration_count

    x = tello.get_mission_pad_distance_x()
    y = tello.get_mission_pad_distance_y()
    z = tello.get_mission_pad_distance_z()

    for i in range(0,loop_count):
        if y >= y_min and y <= y_max:
            break
        else:
            tello.go_xyz_speed_mid(x,1,z,DEFAULT_TELLO_SPEED,mpad_id)
            time.sleep(1)
            x = tello.get_mission_pad_distance_x()
            y = tello.get_mission_pad_distance_y()
            z = tello.get_mission_pad_distance_z()

    for i in range(0,loop_count):
        if x >= x_min and x <= x_max:
            break
        else:
            tello.go_xyz_speed_mid(2,y,z,DEFAULT_TELLO_SPEED,mpad_id)
            time.sleep(1)
            x = tello.get_mission_pad_distance_x()
            y = tello.get_mission_pad_distance_y()
            z = tello.get_mission_pad_distance_z()

def tello_move_to_next_mpad(step, step_count, old_mpad_id):
    loop_count = step_count
    for i in range(0,loop_count):

        tello.move_forward(step)
        new_mpad_id = tello.get_mission_pad_id()
        
        if new_mpad_id > 0 and new_mpad_id != old_mpad_id:
            print("new mission pad found")
            break

def main():
    tello = Tello()
    tello.connect()
    tello.streamon()

    cap = cv2.VideoCapture(tello.get_udp_video_address())

    def video_stream():
        while(1):
            ret, frame = cap.read()

            if not ret :
                cap.release()
                break

            cv2.imshow('Camera',frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    video = threading.Thread(target=video_stream)
    video.start()

    tello.enable_mission_pads()
    tello.set_mission_pad_detection_direction(0)
    tello.takeoff()
    mpad_id = tello.get_mission_pad_id()
    print(mpad_id)

    if mpad_id < 0:
        tello.land()
        exit(-1)
    
    for i in range(0,6):
        tello_position_near_mpad(TOLERANCE_X_AXIS, TOLERANCE_Y_AXIS, mpad_id, POSITIONING_ITERATION_COUNT)
        current_z = tello.get_mission_pad_distance_z()

        if current_z < MINIMUM_HEIGHT_THRESHOLD:
            tello.move_up(DEFAULT_UPWARD_STEP)
        
        tello_move_to_next_mpad(DEFAULT_FORWARD_STEP, int(DEFAULT_FORWARD_STEP_COUNT),mpad_id)
        mpad_id = tello.get_mission_pad_id()

        if current_z >= MINIMUM_HEIGHT_THRESHOLD:
            tello.move_down(DEFAULT_UPWARD_STEP)

        tello.rotate_clockwise(DEFAULT_ROTATION_IN_DEGREE)

    tello_position_near_mpad(TOLERANCE_X_AXIS, TOLERANCE_Y_AXIS, mpad_id, POSITIONING_ITERATION_COUNT)
    tello_position_near_mpad(1, 1, mpad_id, POSITIONING_ITERATION_COUNT)
    tello.land()

    cap.release()

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()