# EyeProtector
This python script uses your webcam to let you know that you did not blink for more than 10 seconds. It is implemented
to work on Ubuntu 18.04.

## How it works?
It uses dlib library to detect your eye lids' position and the uses EAR to detect whether your eyes are closed. If they 
are not closed for more than 10 seconds, it sends notification every 5 seconds. It will close the notification
immediately once you blink.

# Installing and execution
It needs python `>3.6`.

Run `pip3 install -r requirements.txt` to install the required libraries. Then execute the script by running
`./main.py`.

You may need to adjust some variables based on your environment and how your webcam works.
