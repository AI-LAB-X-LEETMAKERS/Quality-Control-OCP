from pypylon import pylon
import cv2

def signle_grab(frames, exposure, gain):
    try:
        factory = pylon.TlFactory.GetInstance()
        devices = factory.EnumerateDevices() # discover the cam
        if not devices:
            print("no camera detected")
            raise Exception()
        convert = pylon.ImageFormatConverter()
        convert.OutputPixelFormat = pylon.PixelType_BGR8packed

        with pylon.InstantCamera(pylon.FirstFound) as cam:
            cam.StartGrabbingMax(frames, pylon.GrabStrategy_OneByOne) 
            count = 1
            cam.Open()
            cam.ExposureAuto.SetValue("Off")
            cam.ExposureTime.SetValue(exposure)
            cam.Gain.SetValue(gain)
            while cam.IsGrabbing():
                with cam.RetrieveResult(5000) as result:
                    if not result.GrabSucceeded():
                        print("error Retrieving from buffer queue")
                        raise Exception()
                    image = convert.ConvertToArray(result) 
                    cv2.imwrite(f"output/image{count}.png", image)
                    count += 1
            cv2.destroyAllWindows()
            print("done")
    except Exception as e:
        print(e)