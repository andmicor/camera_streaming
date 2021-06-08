from flask import Flask, render_template, Response
import cv2
import depthai as dai

app = Flask(__name__)

#camera = cv2.VideoCapture(0)  # use 0 for web camera

def gen_frames():  # generate frame by frame from camera
    while True:
        # Create pipeline
        pipeline = dai.Pipeline()

        # Define source and output
        camRgb = pipeline.createColorCamera()
        xoutVideo = pipeline.createXLinkOut()

        xoutVideo.setStreamName("video")

        # Properties
        camRgb.setBoardSocket(dai.CameraBoardSocket.RGB)
        camRgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
        camRgb.setVideoSize(1920, 1080)

        xoutVideo.input.setBlocking(False)
        xoutVideo.input.setQueueSize(1)

        # Linking
        camRgb.video.link(xoutVideo.input)
        # Connect to device and start pipeline
        with dai.Device(pipeline) as device:

            # Output queue will be used to get the rgb frames from the output defined above
            qRgb = device.getOutputQueue(name="video", maxSize=1, blocking=False)

            while True:
                inRgb = qRgb.get()  # blocking call, will wait until a new data has arrived

                # Retrieve 'bgr' (opencv format) frame
                cv2.imshow("rgb", inRgb.getCvFrame())

                if cv2.waitKey(1) == ord('q'):
                    break
                # Capture frame-by-frame
                frame = inRgb.getCvFrame() # read the camera frame

                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result


@app.route('/video_feed')
def video_feed():
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)