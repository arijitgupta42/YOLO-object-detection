import cv2
import numpy as np 
import time
import sys
import os

CONFIDENCE = 0.5
SCORE_THRESHOLD = 0.5
IOU_THRESHOLD = 0.5

config_path = "cfg/yolov3.cfg"
weights_path = "weights/yolov3.weights"

labels = open("data/coco.names").read().strip().split("\n")
colors = np.random.randint(0, 255, size =(len(labels), 3), dtype='uint8')

net = cv2.dnn.readNetFromDarknet(config_path, weights_path)

def yolo_detect(image):

    h,w = image.shape[:2]
    blob = cv2.dnn.blobFromImage(image, 1/255.0, (416,416), swapRB = True, crop = False)

    net.setInput(blob)
    ln = net.getLayerNames()
    ln = [ln[i[0] - 1] for i in net.getUnconnectedOutLayers()]
    start = time.perf_counter()
    layer_outputs = net.forward(ln)
    time_took = time.perf_counter() - start
    
    font_scale = 1
    thickness = 1
    boxes, confidences, class_ids = [], [], []

    for output in layer_outputs:
       
        for detection in output:

            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]

            if confidence > CONFIDENCE:

                box = detection[:4] * np.array([w, h, w, h])
                (centerX, centerY, width, height) = box.astype("int")

                x = int(centerX - (width / 2))
                y = int(centerY - (height / 2))

                boxes.append([x, y, int(width), int(height)])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    idxs = cv2.dnn.NMSBoxes(boxes, confidences, SCORE_THRESHOLD, IOU_THRESHOLD)

    if len(idxs) > 0:
        
        for i in idxs.flatten():
            
            x, y = boxes[i][0], boxes[i][1]
            w, h = boxes[i][2], boxes[i][3]
            
            color = [int(c) for c in colors[class_ids[i]]]
            cv2.rectangle(image, (x, y), (x + w, y + h), color=color, thickness=thickness)
            text = f"{labels[class_ids[i]]}: {confidences[i]:.2f}"
            print(text)
            
            (text_width, text_height) = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, fontScale=font_scale, thickness=thickness)[0]
            text_offset_x = x
            text_offset_y = y - 5
            box_coords = ((text_offset_x, text_offset_y), (text_offset_x + text_width + 2, text_offset_y - text_height))
            overlay = image.copy()
            cv2.rectangle(overlay, box_coords[0], box_coords[1], color=color, thickness=cv2.FILLED)
            
            image = cv2.addWeighted(overlay, 0.6, image, 0.4, 0)
            
            cv2.putText(image, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=font_scale, color=(0, 0, 0), thickness=thickness)

    return image

path_name = "images/street.jpg"
image = cv2.imread(path_name)
file_name = os.path.basename(path_name)
filename, ext = file_name.split(".")
image = yolo_detect(image)
cv2.imwrite("results/" + filename +"_yolo3." + ext, image )