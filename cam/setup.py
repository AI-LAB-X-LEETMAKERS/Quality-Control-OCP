from pypylon import pylon
import cv2

try:
    factory = pylon.TlFactory.GetInstance()
    devices = factory.EnumerateDevices() # discover the cam
    if not devices:
        print("no camera detected")
        raise Exception()
    print(f"{devices[0].GetFriendlyName()}")
    device = factory.CreateDevice(devices[0])

    with pylon.InstantCamera(device) as cam: #open the cam 
        cam.StartGrabbingMax(pylon.GrabStrategy_LatestImageOnly)
        while cam.IsGrabbing():
            with cam.RetrieveResult(5000) as result:
                if not result.GrabSucceeded():
                    print("error Retrieving from buffer queue")
                    raise Exception()
                image = result.Array # make sure to copy using Array to use later...i need to remind myself of that for sure
                print(image.shape) # the Array basically is a Numpy array and Shape represent the metadata (W,H)
                print(image.dtype)
                print(result.PixelType)
                cv2.imwrite("output/image.png", image)
                cv2.imshow("basler", image)
                if cv2.waitKey(1) == 27:
                    break
        cv2.destroyAllWindows()
except Exception as e:
    print(e)

if __name__ == "__main__":
    pass