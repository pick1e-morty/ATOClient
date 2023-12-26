import time
from pathlib import Path
from UnifyNetSDK import HaikangPlaySDK

playClient = HaikangPlaySDK()
nPort = playClient.getFreePort()
videoPath = "test.mp4"
playClient.openFile(nPort, videoPath)
playClient.play(nPort)

time.sleep(0.1)

absPath = Path(__file__).absolute()
absPicName = absPath.with_name("test.jpg")
# playClient.catchPic(nPort, absPicName)
playClient.catchPic(nPort, absPicName, quality=100)

playClient.stop(nPort)
playClient.close(nPort)
playClient.releasePort(nPort)
