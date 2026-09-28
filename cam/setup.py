from pypylon import pylon
import cv2

try:
    factory = pylon.TlFactory.GetInstance()
    devices = factory.EnumerateDevices() # discover the cam
    if not devices:
        print("no camera detected")
        raise Exception()
    print(f"{devices[0].GetFriendlyName()}")
    print(f"{devices[0].GetSerialNumber()}")

    with pylon.InstantCamera(pylon.FirstFound) as cam:  
        cam.StartGrabbingMax(30, pylon.GrabStrategy_OneByOne) 
        count = 1
        print("Capturing images...")
        while cam.IsGrabbing():
            with cam.RetrieveResult(5000) as result:
                if not result.GrabSucceeded():
                    print("error Retrieving from buffer queue")
                    raise Exception()
                image = result.Array 
                cv2.imwrite(f"output/image{count}.png", image)
                count += 1
        cv2.destroyAllWindows()
        print("done")
except Exception as e:
    print(e)

if __name__ == "__main__":
    pass