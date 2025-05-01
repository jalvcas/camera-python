from cv2 import VideoCapture, imwrite, imshow, destroyWindow, waitKey

cam_port = 0  # Change this to the correct port if needed
cam = VideoCapture(cam_port)

result, image = cam.read()

if result:

    imshow("CapturedImage", image)

    imwrite("captured_image.png", image)  # Save the captured image

    waitKey(0)  # Wait for a key press to close the window
    destroyWindow("CapturedImage")

else:
    print("Failed to capture image")