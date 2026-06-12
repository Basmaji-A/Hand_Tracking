# Import OpenCV for camera and image
import cv2

# Import MediaPipe for hand tracking
import mediapipe as mp

# Import time to count FPS
import time

# Import math for distance calculation
import math

# Import NumPy for number mapping
import numpy as np

# Import tools to control system sound
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


# Get speaker device
devices = AudioUtilities.GetSpeakers()

# Activate speaker interface
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)

# Cast interface to volume control
volume = cast(interface, POINTER(IAudioEndpointVolume))

# Get volume range (min, max, step)
volRange = volume.GetVolumeRange()

# Save minimum volume
minVol = volRange[0]

# Save maximum volume
maxVol = volRange[1]


# Create a class for hand detection
class handDetector:

    # Initialize the class
    def __init__(self, mode=False, maxHands=1, detectionCon=0.7, trackCon=0.7):

        # Set image mode
        self.mode = mode

        # Set maximum hands
        self.maxHands = maxHands

        # Set detection confidence
        self.detectionCon = detectionCon

        # Set tracking confidence
        self.trackCon = trackCon

        # Load MediaPipe hands solution
        self.mpHands = mp.solutions.hands

        # Create hands object
        self.hands = self.mpHands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.maxHands,
            min_detection_confidence=self.detectionCon,
            min_tracking_confidence=self.trackCon,
        )

        # Load drawing tools
        self.mpDraw = mp.solutions.drawing_utils

        # Finger tip landmark IDs
        self.tipIds = [4, 8, 12, 16, 20]

    # Find hands in image
    def findHands(self, img, draw=True):

        # Convert image to RGB
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Process image with MediaPipe
        self.results = self.hands.process(imgRGB)

        # If hands are found
        if self.results.multi_hand_landmarks:

            # Loop through all hands
            for handLms in self.results.multi_hand_landmarks:

                # Draw hand landmarks
                if draw:
                    self.mpDraw.draw_landmarks(
                        img, handLms, self.mpHands.HAND_CONNECTIONS
                    )

        # Return image
        return img

    # Get hand position
    def findPosition(self, img, handNo=0, draw=True):

        # List for x values
        xList = []

        # List for y values
        yList = []

        # Bounding box list
        bbox = []

        # Landmark list
        self.lmList = []

        # If hand landmarks exist
        if self.results.multi_hand_landmarks:

            # Select one hand
            myHand = self.results.multi_hand_landmarks[handNo]

            # Loop through landmarks
            for id, lm in enumerate(myHand.landmark):

                # Get image size
                h, w, c = img.shape

                # Convert to pixel position
                cx, cy = int(lm.x * w), int(lm.y * h)

                # Save x and y
                xList.append(cx)
                yList.append(cy)

                # Save landmark id and position
                self.lmList.append([id, cx, cy])

                # Draw landmark point
                if draw:
                    cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)

            # Get box limits
            xmin, xmax = min(xList), max(xList)
            ymin, ymax = min(yList), max(yList)

            # Save bounding box
            bbox = xmin, ymin, xmax, ymax

            # Draw bounding box
            if draw:
                cv2.rectangle(
                    img,
                    (bbox[0] - 20, bbox[1] - 20),
                    (bbox[2] + 20, bbox[3] + 20),
                    (0, 255, 0),
                    2,
                )

        # Return landmarks and box
        return self.lmList, bbox

    # Find distance between two points
    def findDistance(self, p1, p2, img, draw=True):

        # Get first point
        x1, y1 = self.lmList[p1][1], self.lmList[p1][2]

        # Get second point
        x2, y2 = self.lmList[p2][1], self.lmList[p2][2]

        # Get center point
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        # Draw points and line
        if draw:
            cv2.circle(img, (x1, y1), 10, (0, 255, 0), cv2.FILLED)
            cv2.circle(img, (x2, y2), 10, (0, 255, 0), cv2.FILLED)
            cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 3)
            cv2.circle(img, (cx, cy), 10, (0, 0, 255), cv2.FILLED)

        # Calculate distance
        length = math.hypot(x2 - x1, y2 - y1)

        # Return distance and data
        return length, img, [x1, y1, x2, y2, cx, cy]


# Main function
def main():

    # Previous time
    pTime = 0

    # Open camera
    cap = cv2.VideoCapture(0)

    # Create hand detector
    detector = handDetector()

    # Volume bar position
    volBar = 400

    # Volume percent
    volPer = 0

    # Loop forever
    while True:

        # Read camera frame
        success, img = cap.read()

        # If frame not read
        if not success:
            break

        # Find hands
        img = detector.findHands(img)

        # Find hand landmarks
        lmList, bbox = detector.findPosition(img)

        # If hand is detected
        if len(lmList) != 0:

            # Get distance between thumb and index
            length, img, _ = detector.findDistance(4, 8, img)

            # Map distance to volume level
            vol = np.interp(length, [20, 200], [minVol, maxVol])

            # Map distance to volume bar
            volBar = np.interp(length, [20, 200], [400, 150])

            # Map distance to percentage
            volPer = np.interp(length, [20, 200], [0, 100])

            # Set system volume
            volume.SetMasterVolumeLevel(vol, None)

        # Draw volume bar outline
        cv2.rectangle(img, (50, 150), (85, 400), (0, 0, 0), 3)

        # Draw volume bar fill
        cv2.rectangle(img, (50, int(volBar)), (85, 400), (0, 255, 0), cv2.FILLED)

        # Show volume percent
        cv2.putText(
            img,
            f"{int(volPer)} %",
            (40, 430),
            cv2.FONT_HERSHEY_PLAIN,
            2,
            (255, 0, 0),
            3,
        )

        # Current time
        cTime = time.time()

        # Calculate FPS
        fps = 1 / (cTime - pTime) if cTime != pTime else 0

        # Update previous time
        pTime = cTime

        # Show FPS
        cv2.putText(
            img,
            f"FPS: {int(fps)}",
            (400, 70),
            cv2.FONT_HERSHEY_PLAIN,
            2,
            (255, 0, 255),
            2,
        )

        # Show window
        cv2.imshow("Gesture Volume Control", img)

        # Exit when press q
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break


# Run main function
if __name__ == "__main__":
    main()
