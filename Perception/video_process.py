import cv2

# 这里假设 RTFS 可以通过 URL 或者本地文件访问
cap = cv2.VideoCapture("rtsp://admin:admin@sk.yunenjoy.cn:35201/main.264")



while True:
    ret, frame = cap.read()
    if not ret:
        break

    # frame 已经是 BGR (OpenCV 默认) 图像，可以直接处理
    cv2.imshow("frame", frame)

    # SLAM 需要灰度图
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    if cv2.waitKey(1) == 27:  # ESC 退出
        break

cap.release()
cv2.destroyAllWindows()