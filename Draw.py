import cv2
import mediapipe as mp
import numpy as np
import math

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

canvas = np.zeros((720, 1280, 3), dtype=np.uint8)
colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (0, 0, 0)]
color_names = ['Blue', 'Green', 'Red', 'Eraser']
tools = ['Pen', 'Circle', 'Rectangle', 'Clear', 'Save']

current_tool = 'Pen'
current_color = colors[0]
brush_size = 8

draw_point = None
shape_start = None
shape_preview = None
dragging_shape = None
draw_history = []

tool_buttons = {tool: (20 + i * 100, 20) for i, tool in enumerate(tools)}
color_buttons = [(20 + i * 60, 100) for i in range(len(colors))]

def check_click_with_left_hand(x, y):
    global current_tool, current_color, canvas, draw_history
    for tool, (bx, by) in tool_buttons.items():
        if bx < x < bx + 80 and by < y < by + 50:
            if tool == 'Clear':
                canvas[:] = 0
                draw_history.clear()
                current_tool = 'Pen'
            elif tool == 'Save':
                cv2.imwrite("drawing_output.png", canvas)
            else:
                current_tool = tool
    for i, (cx, cy) in enumerate(color_buttons):
        if cx < x < cx + 50 and cy < y < cy + 50:
            current_color = colors[i]
            current_tool = 'Pen'

def count_fingers(hand_landmarks):
    fingers = []
    tip_ids = [4, 8, 12, 16, 20]
    fingers.append(1 if hand_landmarks.landmark[tip_ids[0]].x < hand_landmarks.landmark[tip_ids[0] - 1].x else 0)
    for i in range(1, 5):
        fingers.append(1 if hand_landmarks.landmark[tip_ids[i]].y < hand_landmarks.landmark[tip_ids[i] - 2].y else 0)
    return sum(fingers)

def get_distance(p1, p2):
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

def point_inside_shape(pt, shape):
    if shape[0] == 'circle':
        return get_distance(pt, shape[1]) < shape[2]
    elif shape[0] == 'rectangle':
        x1, y1 = shape[1]
        x2, y2 = shape[2]
        return x1 <= pt[0] <= x2 and y1 <= pt[1] <= y2
    return False

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    h, w, _ = frame.shape
    left_hand, right_hand = None, None
    left_pos, right_pos = None, None

    if results.multi_hand_landmarks and results.multi_handedness:
        for i, hand_landmark in enumerate(results.multi_hand_landmarks):
            label = results.multi_handedness[i].classification[0].label
            if label == 'Right':
                right_hand = hand_landmark
            else:
                left_hand = hand_landmark

    # Left hand: gesture, selection, draw landmarks
    if left_hand:
        mp_draw.draw_landmarks(frame, left_hand, mp_hands.HAND_CONNECTIONS)
        if (left_hand.landmark[8].y < left_hand.landmark[6].y and
            left_hand.landmark[12].y < left_hand.landmark[10].y):
            if draw_history:
                draw_history.pop()
                canvas[:] = 0
                for item in draw_history:
                    if item[0] == 'line':
                        cv2.line(canvas, item[1], item[2], item[3], item[4], cv2.LINE_AA)
                    elif item[0] == 'circle':
                        cv2.circle(canvas, item[1], item[2], item[3], item[4])
                    elif item[0] == 'rectangle':
                        cv2.rectangle(canvas, item[1], item[2], item[3], item[4])
        lx, ly = int(left_hand.landmark[8].x * w), int(left_hand.landmark[8].y * h)
        check_click_with_left_hand(lx, ly)

    if right_hand:
        mp_draw.draw_landmarks(frame, right_hand, mp_hands.HAND_CONNECTIONS)
        x = int(right_hand.landmark[8].x * w)
        y = int(right_hand.landmark[8].y * h)
        right_pos = (x, y)

        thumb = int(right_hand.landmark[4].x * w), int(right_hand.landmark[4].y * h)
        brush_size = int(get_distance(thumb, right_pos) / 4)
        brush_size = max(2, min(50, brush_size))

        if current_tool == 'Pen':
            if draw_point:
                color = current_color
                thickness = 40 if current_color == (0, 0, 0) else brush_size
                cv2.line(canvas, draw_point, right_pos, color, thickness)
                draw_history.append(('line', draw_point, right_pos, color, thickness))
            draw_point = right_pos

        elif current_tool in ['Circle', 'Rectangle']:
            if not shape_start:
                shape_start = right_pos
            else:
                shape_preview = (shape_start, right_pos)

        else:
            draw_point = None
            shape_start = None
            shape_preview = None
    else:
        draw_point = None
        shape_start = None
        shape_preview = None

    # Draw preview shape
    frame_display = canvas.copy()
    if shape_preview:
        pt1, pt2 = shape_preview
        if current_tool == 'Circle':
            radius = int(get_distance(pt1, pt2))
            cv2.circle(frame_display, pt1, radius, current_color, 2)
        elif current_tool == 'Rectangle':
            cv2.rectangle(frame_display, pt1, pt2, current_color, 2)

    if shape_preview and right_hand and count_fingers(right_hand) < 2:
        pt1, pt2 = shape_preview
        if current_tool == 'Circle':
            radius = int(get_distance(pt1, pt2))
            cv2.circle(canvas, pt1, radius, current_color, 4)
            draw_history.append(('circle', pt1, radius, current_color, 4))
        elif current_tool == 'Rectangle':
            cv2.rectangle(canvas, pt1, pt2, current_color, 4)
            draw_history.append(('rectangle', pt1, pt2, current_color, 4))
        shape_preview = None
        shape_start = None

    # Drag shapes
    if right_pos and dragging_shape is None and current_tool not in ['Circle', 'Rectangle']:
        for i in range(len(draw_history)-1, -1, -1):
            item = draw_history[i]
            if item[0] in ['circle', 'rectangle'] and point_inside_shape(right_pos, item):
                dragging_shape = i
                break

    if dragging_shape is not None and right_pos:
        item = draw_history[dragging_shape]
        if item[0] == 'circle':
            draw_history[dragging_shape] = ('circle', right_pos, item[2], item[3], item[4])
        elif item[0] == 'rectangle':
            w_diff = item[2][0] - item[1][0]
            h_diff = item[2][1] - item[1][1]
            new_pt1 = right_pos
            new_pt2 = (new_pt1[0] + w_diff, new_pt1[1] + h_diff)
            draw_history[dragging_shape] = ('rectangle', new_pt1, new_pt2, item[3], item[4])
        canvas[:] = 0
        for item in draw_history:
            if item[0] == 'line':
                cv2.line(canvas, item[1], item[2], item[3], item[4], cv2.LINE_AA)
            elif item[0] == 'circle':
                cv2.circle(canvas, item[1], item[2], item[3], item[4])
            elif item[0] == 'rectangle':
                cv2.rectangle(canvas, item[1], item[2], item[3], item[4])

    if right_hand and count_fingers(right_hand) > 3:
        dragging_shape = None

    # UI
    frame_display = cv2.addWeighted(frame, 0.3, frame_display, 0.7, 0)
    for tool, (bx, by) in tool_buttons.items():
        color = (0, 255, 255) if current_tool == tool else (255, 255, 255)
        cv2.rectangle(frame_display, (bx, by), (bx + 80, by + 50), color, 2)
        cv2.putText(frame_display, tool, (bx + 5, by + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    for i, (cx, cy) in enumerate(color_buttons):
        cv2.rectangle(frame_display, (cx, cy), (cx + 50, cy + 50), colors[i], -1)
        cv2.rectangle(frame_display, (cx, cy), (cx + 50, cy + 50), (255, 255, 255), 2)

    cv2.putText(frame_display, f'Brush Size: {brush_size}', (1000, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 2)

    cv2.imshow("Advanced Two-Handed Drawing App", frame_display)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
