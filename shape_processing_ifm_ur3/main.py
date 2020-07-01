import ifm3dpy
import cv2
from shape_recognition import shape_recognition
from shape_size import shape_size
from Camera import Camera
from Shape import Shape
from ur3 import get_object, GUI_Positions

def main():
    cam = Camera.Camera()
    try:
        im = cam.get_image()
    except RuntimeError as e:
        print(e)
        return -1
    cv2.imwrite("detectedShape.png",im.amplitude_image())
    cont, img, detected, center, angle = shape_recognition(Shape.Shape.RECTANGLE,"detectedShape.png")
    height, length, width = shape_size(cont, im.distance_image())
    cv2.imwrite("detectedShape.png",img)

    print("Detected : ", detected)
    print("Height : ",height," Length : ",length, " Width : ",width)

    app = GUI_Positions()
    dic = app.get_pos()
    img_height, img_width = img.shape
    get_object(dic,img_width,img_height,center,height,angle)

if __name__=='__main__':
    main()

