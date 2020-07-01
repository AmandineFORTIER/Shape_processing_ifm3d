import cv2
import numpy as np
from shape_recognition import shape_recognition
from Shape import Shape
from Camera import Camera
import math

def shape_size(contour,dist):
    """
    Get the shape size.

    Get the height, width and length of the shape.

    Parameters
    ----------
    contour : numpy.ndarray
        The object's contours.
    dist : numpy.ndarray
        The distance image
    
    Returns
    -------
    height : float
        The object height in meters
    length : float
        The object length in meters
    width: float
        The object width in meters
    """
    try:  
        if(contour.size == 0):
            raise ValueError('Contours can not be empty. I can not calculate the object size.')
    except Exception as e:
        print(e)
        return None, None, None
    height = __get_height(contour,dist)
    length, width = __get_length_width(contour,dist)
    return  height, length, width


def __get_length_width(contour, dist):
    """
    Get the shape length and width.

    Get the length and width of the shape.

    Parameters
    ----------
    contour : numpy.ndarray
        The object's contours.
    dist : numpy.ndarray
        The distance image
    
    Returns
    -------
    obj_length : float
        The object length in meters
    obj_width: float
        The object width in meters
    """
    _, (width, length), angle = cv2.minAreaRect(contour)
    if(width > length):
        tmp = length
        length = width
        width = tmp

    _, x2 = dist.shape
    a = dist[0,0]
    b = dist[0,x2-1]
    angle = 40 
    c = math.sqrt(a**2 + b**2 - 2*a*b*math.cos(math.radians(angle))) # Al-Kashi

    pixel_size = c/x2
    obj_length = length*pixel_size
    obj_width = width*pixel_size
    return obj_length, obj_width

def __get_height(contour,dist):
    """
    Get the shape height.

    Get the height of the shape.

    Parameters
    ----------
    contour : numpy.ndarray
        The object's contours.
    dist : numpy.ndarray
        The distance image
    
    Returns
    -------
    height : float
        The object height in meters
    """
    object_mask, object_dist = __object_distance(contour, dist) 
    floor_dist = __floor_distance(contour, dist, object_mask)
    height = floor_dist-object_dist   
    return height

def __floor_distance(contour, dist, mask):
    """
    Detect the distance between the floor and the Camera.

    Takes the mean distance of the object's contour.

    Parameters
    ----------
    contour : numpy.ndarray
        The object's contours.
    dist : numpy.ndarray
        The distance image
    mask : numpy.ndarray
        The object

    Returns
    -------
    mean_dist : float
        The mean distance of the floor.
    """
    mask_out = np.zeros(dist.shape,np.uint8)
    cont_out = cv2.minAreaRect(contour)
    cont_out = cv2.boxPoints(cont_out)
    cont_out = np.int0(cont_out)
    cv2.drawContours(mask_out, [cont_out], -1, (255), -1)
    mask_out = cv2.dilate(mask_out,(5,5),iterations=10)
    mask = cv2.dilate(mask,(3,3),iterations=2)
    mask_out-=mask
    mean = cv2.mean(dist,mask_out)
    mean_dist = mean[0]
    return mean_dist

def __object_distance(contour, dist):
    """
    Detect the distance between an object and the Camera.

    Takes the mean distance of the object.

    Parameters
    ----------
    contour : numpy.ndarray
        The object's contours.
    dist : numpy.ndarray
        The distance image
    
    Returns
    -------
    mask : numpy.ndarray
        The object
    mean_dist : float
        The mean distance of the object.
    """
    mask = np.zeros(dist.shape,np.uint8)
    cv2.drawContours(mask, [contour], -1, (255), -1)
    mean = cv2.mean(dist,mask)
    mean_dist = mean[0] 
    return mask, mean_dist

def main():
    cam = Camera()
    try:
        im = cam.get_image()
    except RuntimeError as e:
        print(e)
        return -1
    dist = im.distance_image()
    cv2.imwrite("preview.png",im.amplitude_image())
    contour, img, _,_,_ = shape_recognition(Shape.RECTANGLE,"preview.png")
    cv2.imwrite("detectedShape.png",img)
    h,w,l = shape_size(contour,dist)
    print("Object height : ",h)
    print("Object width : ",w)
    print("Object length : ",l)
    return 0

if __name__=='__main__':
    main()