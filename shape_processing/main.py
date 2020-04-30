import ifm3dpy
import cv2
import shape_recognition
import shape_size
import Camera
import Shape

def main():
    cam = Camera.Camera()
    try:
        im = cam.get_image()
    except RuntimeError as e:
        print(e)
        return -1
    cv2.imwrite("detectedShape.png",im.amplitude_image())
    cont, img, detected = shape_recognition.shape_recognition(Shape.Shape.RECTANGLE,"detectedShape.png")
    height, length, width = shape_size.shape_size(cont, im.distance_image())
    cv2.imwrite("detectedShape.png",img)

    print("Detected : ", detected)
    print("Height : ",height," Length : ",length, " Width : ",width)


if __name__=='__main__':
    main()

