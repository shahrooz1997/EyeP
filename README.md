# EyeProtector

This python script uses your webcam to let you know that you did not blink for more than 10 seconds. It is implemented
to work on Ubuntu 18.04.

## How it works?

It uses dlib library to detect your eye lids' landmarks [1] and then uses EAR [2] to detect whether your eyes are
closed. If they are not closed for more than 10 seconds, it sends notification every 5 seconds. It will close the
notification immediately once you blink.

If no eyes are detected for more than 3 minutes, it turns off your webcam for 15 minutes and then retry. It helps to
save costs for cases when you leave your system.

## Installing and execution

It needs python `>3.6`.

Run `python3 -m pip install -r requirements.txt` to install the required libraries. If you hit error during the
execution of that command, you may need to run `python3 -m pip install --upgrade pip` and then retry. Then, execute the
script by running `python3 ./main.py`.

You may need to adjust some variables based on your environment and how your webcam works.

## Todos

* Add support for other operating systems (Windows and macOS)
* Add a notification to follow 20/20/20 rule. (After looking at the monitor for 20 minutes, you should look at a point
  that is at lear 20 feet far for 20 seconds)

## Contribution

Please let me know how I can improve it at [shahrooz.1000@gmail.com](mailto:shahrooz.1000@gmail.com).

## References

[1] V. Kazemi and J. Sullivan, "One millisecond face alignment with an ensemble of regression trees," 2014 IEEE
Conference on Computer Vision and Pattern Recognition, 2014, pp. 1867-1874, doi: 10.1109/CVPR.2014.241.

[2] Soukupová, Tereza and Jan Cech. “Real-Time Eye Blink Detection using Facial Landmarks.” (2016).
