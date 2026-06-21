"""
TODO: Figure out a cool demo?
TODO: Segment it into functions :)
TODO: If the fingers are held it holds the clicking
"""

import cv2
import mediapipe as mp
import math
from pynput import mouse, keyboard

mouse_controller = mouse.Controller()

track = False

line = False

#handles monitoring keyboard presses
def on_press(key):
    global track
    global line
    try:
        if key.char == "k":
            track = not track
            print("Track: " +str(track))
        
        if key.char == "l":
            line = not line
            print("Show Line: " + str(line))

    except AttributeError:
        # Handles special keys like shift, ctrl, etc. so they don't crash your script
        pass

listener = keyboard.Listener(on_press=on_press)
listener.start()

#Webcam and window setup
cap = cv2.VideoCapture(0) #0 for webcam and video for video
cv2.namedWindow("ME BABYYY", cv2.WINDOW_NORMAL)
cv2.setWindowProperty("ME BABYYY", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)

#makes writing stuff easier
mp_drawing = mp.solutions.drawing_utils # type: ignore
mp_hands = mp.solutions.hands # type: ignore
hand = mp_hands.Hands(max_num_hands=1) 

prev_x = None
prev_y = None

prev_l_click = False
prev_r_click = False

mouse_move = False

mv_text = ""

mid_x = None
mid_y = None

mouse_sens = 10
smooth = 0.25

mv_left = False
mv_right = False
mv_up = False
mv_down = False

def draw_ui():
    global click, r_click, track, line, frame, mv_text
    global thumb_x, thumb_y, index_x, index_y, middle_x, middle_y, wrist_x, wrist_y

    #* Text Code
    click_text  = "Click: " +  str(click)
    r_click_text = "Right Click: " +  str(r_click)
    cv2.putText(frame, mv_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2) #text for movement direction
    cv2.putText(frame,click_text , (225, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2) # text for clicking
    cv2.putText(frame, r_click_text , (225, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2) #text for right click

    track_text = "Track:" + str(track)
    cv2.putText(frame, track_text, (10, 75), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    if line:
        cv2.line(frame, (int(thumb_x),int(thumb_y)), (int(index_x), int(index_y)), (255,0,0),5) # line berween index and thumb
        cv2.line(frame, (int(middle_x),int(middle_y)), (int(wrist_x), int(wrist_y)), (0,255,0),5) # line between middle and wrist

def handle_mouse():
    global prev_x, prev_y, mid_x, mid_y, mouse_sens, smooth, mouse_move

    if mouse_move:    
        if prev_x != None and prev_y != None:
            mouse_x = int(mid_x) - int(prev_x) 
            mouse_y = int(mid_y) - int(prev_y)
            mouse_controller.move(
            
            int((int(mid_x) - int(prev_x)) * smooth * mouse_sens),
            int((int(mid_y) - int(prev_y)) * smooth * mouse_sens) 
            
            )

            prev_x, prev_y = prev_x + (mid_x - prev_x) * smooth, prev_y + (mid_y - prev_y) * smooth
        else:
            prev_x, prev_y = mid_x, mid_y
def handle_click():
    global click, r_click, prev_l_click, prev_r_click, mouse_move
    global d_l_click, d_r_click, d_mouse

    
    if d_l_click < 25:
    

        if prev_l_click == False:
            click = True
        else:
            click = False     

        prev_l_click = True
    else:
        prev_l_click = False
        click = False


    if d_r_click < 25:
        
        if prev_r_click == False:
            r_click = True
        else:
            r_click = False
        
        prev_r_click = True
    else:
        prev_r_click = False
        r_click = False

        if d_mouse < 55:
            mouse_move = True
        else:
            mouse_move = False
            prev_x, prev_y = None, None

    if click:
        mouse_controller.press(mouse.Button.left)
        mouse_controller.release(mouse.Button.left)

    if r_click:
        mouse_controller.press(mouse.Button.right)
        mouse_controller.release(mouse.Button.right)



while True:
    click = False
    r_click = False

    success, frame = cap.read() #Open CV reads as BGR
    frame = cv2.flip(frame,1) #1 just means mirror

    h, w, _ = frame.shape

    if success:
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hand.process(rgb_frame) #mp reads as RGB 

        if result.multi_hand_landmarks:
            for landmark in result.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, landmark, mp_hands.HAND_CONNECTIONS)

                totalx = 0
                totaly = 0
                for point in landmark.landmark:
                    totalx += point.x
                    totaly += point.y

                avg_x = totalx/21
                avg_y = totaly/21

                #middle of the hand
                mid_x = int(avg_x * w)
                mid_y = int(avg_y * h)


                cv2.circle(frame, (mid_x, mid_y), 10, (0, 0, 255), -1)

                #Get the coord for fingers
                index = landmark.landmark[8]
                thumb = landmark.landmark[4]
                middle = landmark.landmark[12]
                wrist = landmark.landmark[0]

                index_x = index.x*w
                index_y = index.y*h

                middle_x = middle.x*w
                middle_y = middle.y*h

                wrist_x = wrist.x*w
                wrist_y = wrist.y*h

                thumb_x = thumb.x*w
                thumb_y = thumb.y*h

                #calc the distance between the index and the thumb
                d_l_click = math.sqrt((index_x - thumb_x)**2 + (index_y - thumb_y)**2)

                #calc the distance between the middle finger and wrist
                d_mouse = math.sqrt((wrist_x - middle_x)**2 + (wrist_y - middle_y)**2)

                #calc the distance between the middle finger and thumb
                d_r_click = math.sqrt((thumb_x - middle_x)**2 + (thumb_y - middle_y)**2)

                            

        if track:

            handle_mouse()

            handle_click()


        draw_ui()

        cv2.imshow("ME BABYYY", frame)
        if cv2.waitKey(1) == ord("q"):
            break

cv2.destroyAllWindows()