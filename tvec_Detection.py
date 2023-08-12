# marker 3d detection
import cv2 as cv
import numpy as np
import socket

# Read the camera calibration parameters from the file
calibration_file = "calibration_params.txt"
with open(calibration_file, "r") as file:
    lines = file.readlines()

camera_matrix_line = lines[1].split(":")[1].strip()
distortion_coefficients_line = lines[3].split(":")[1].strip()

# Parse camera matrix data
camera_matrix_data = [float(x) for x in camera_matrix_line.split(",")]
camera_matrix = np.array(camera_matrix_data).reshape((3, 3))

# Parse distortion coefficients data
distortion_coefficients_data = [float(x) for x in distortion_coefficients_line.split(",")]
distortion_coefficients = np.array(distortion_coefficients_data).reshape((1, 5))


marker_dict = cv.aruco.getPredefinedDictionary(cv.aruco.DICT_4X4_50)

param_markers = cv.aruco.DetectorParameters()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverAddressPort = ("127.0.0.1", 5052)

cap = cv.VideoCapture(0)

success, img = cap.read()
h, w, _ = img.shape

# Known marker information
marker_ids = [6]
focal_length = 600  # cm
wrist_marker = 3.7  # cm
finger_marker = 1.8  # cm

# Initialize x, y, z values for each marker
marker_values = []
for _ in range(len(marker_ids)):
    marker_values.extend([0, 0, 0])

while True:
    ret, frame = cap.read()
    if not ret:
        break
    gray_frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    marker_corners, marker_IDs, _ = cv.aruco.detectMarkers(
        gray_frame, marker_dict, parameters=param_markers
    )

    # Update marker values if markers are detected
    if marker_corners:
        for ids, corners in zip(marker_IDs, marker_corners):
            # Only consider the first marker of a given id
            if ids[0] in marker_ids:

                # Estimate the pose of the marker
                rvec, tvec, _ = cv.aruco.estimatePoseSingleMarkers(corners, wrist_marker, camera_matrix,
                                                                   distortion_coefficients)
                cv.polylines(
                    frame, [corners.astype(np.int32)], True, (0, 255, 255), 4, cv.LINE_AA
                )
                # Draw the marker and its axis on the frame
                # cv.aruco.drawDetectedMarkers(frame, corners)
                #cv.drawFrameAxes(frame, camera_matrix, distortion_coefficients, rvec, tvec, 0.1)
                #print("rvec: ")
                #print(rvec)
                #print("\n\n")
                #print("tvec: ")
                #print(tvec)
                # Update marker values
                marker_values[0] = tvec[0][0][0]
                marker_values[1] = tvec[0][0][1]  # h - y because in unity the y-axis is the opposite of opencv
                marker_values[2] = tvec[0][0][2]

    # send marker values to unity
    print(marker_values)
    sock.sendto(str.encode(str(marker_values)), serverAddressPort)
    cv.imshow("frame", frame)
    key = cv.waitKey(1)
    if key == ord("q"):
        break

cap.release()
cv.destroyAllWindows()
