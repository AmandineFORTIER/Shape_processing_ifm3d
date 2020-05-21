import ifm3dpy
import cv2
import shape_recognition
import shape_size
import Camera
import Shape
import ur3

def main():
    cam = Camera.Camera()
    try:
        im = cam.get_image()
    except RuntimeError as e:
        print(e)
        return -1
    cv2.imwrite("detectedShape.png",im.amplitude_image())
    cont, img, detected, center, angle = shape_recognition.shape_recognition(Shape.Shape.RECTANGLE,"detectedShape.png")
    height, length, width = shape_size.shape_size(cont, im.distance_image())
    cv2.imwrite("detectedShape.png",img)

    print("Detected : ", detected)
    print("Height : ",height," Length : ",length, " Width : ",width)

    app = ur3.GUI_Positions()
    dic = app.get_pos()
    img_height, img_width = img.shape
    ur3.get_object(dic,img_width,img_height,center,height,angle)

if __name__=='__main__':
    main()

