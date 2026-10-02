Motion Detection System

How it works:

1- read the settings from xml file (video path,threshold, min area).
2-The first frame is used as the background reference.
3-Each frame is converted to grayscale and blurred to reduce noise.
4-The difference between the current frame and the background is calculated.
5-A threshold is applied to get a binary image (white = motion, black = no motion).
6-The number of white pixels is counted as the motion score.
7-If the score is above min area, the frame is marked as ALERT.
8-Contours are detected and a green rectangle is drawn around moving objects.

DSA used:
A deque (from collections) with maxlen=10 is used to store the last 10 motion scores.
why?
1-By taking the average of the last 10 frames, the status becomes more stable.

2-deque is used instead of a normal list because it automatically removes the oldest element when it reaches maxlen, which is O(1) instead of O(n).

Requirements
OpenCV numpy pandas s lxml psycopg2-binary pymongo SQLAlchemy tables


Files
main.py - the main script
config.xml - settings file
video/test_video.mp4 - the input video
myfile.pkl - saved background (generated)
motion_archive.h5 - HDF5 output (generated)

How to Run
1-Put the video file inside the video folder.

2-Make sure PostgreSQL and MongoDB are running.

3-Run: python main.py

Output
PostgreSQL: only frames with Status = ALERT

MongoDB: all frames

HDF5: full archive for analysis
 
Each record has: Frame_id, Motion_Score, Avg_Score, Status                                                                                                                                                                                                                    note: iam used PostgreSQL and MongoDB because for learning purposes
       , and this project is Designated for an empty factory at night.
