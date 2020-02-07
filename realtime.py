import cv2
from yolo import yolo_detect

cap = cv2.VideoCapture(0)
if not(cap.isOpened()):
	print("Could not open video device")

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

while(True):
	ret, frame = cap.read()
	cv2.imshow('stream', frame)
	frame = yolo_detect(frame)
	cv2.imshow('yolo stream', frame)

	if cv2.waitKey(1) & 0xFF == ord('q'):
		break
cap.release()
cv2.destroyAllWindows()