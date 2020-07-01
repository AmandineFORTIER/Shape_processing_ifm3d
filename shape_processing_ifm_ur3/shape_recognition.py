import cv2
import sys
import argparse
import numpy as np
from math import pi
from Shape import Shape

def shape_recognition(shape,path):
    """
    Detects different types of shapes on an image.

    We choose an image and a shape.\n
    The algorithm will detect the position, center, and angle of the shape we've chosen.\n
    If the shape is "ALL", "PARTIAL" or "UNKNOW", no position, center, or angle will be returned.

    Parameters
    ----------
    shape : Shape
        The shape we want to detect
    path : str
        The path of the image.

    Returns
    -------
    last_cont : numpy.ndarray
        Contours of the shape. Or an empty array if the shape is ALL, PARTIAL or UNKNOW
    img : numpy.ndarray
        The image with the detected shape and it's name.
    detected_shapes : list
        The detected shapes.
    center : tuple of float
        Center of the detected shape.
    angle : float
        Angle of rotation of the detected shape.
    """
    img = __processing(path)
    if shape is None:
        try:
            raise AttributeError('Shape cannot be None')
        except AttributeError as e:
            print(e)
            return None, img, None
    shape = shape.value
    height, width = img.shape
    img = __fill_holes(height, width, img)

    detected,last_cont, detected_shape, center, angle = __detect_shape(img, height, width, shape)
    last_cont = __useless_contour(shape, detected, last_cont,center,angle)
    return last_cont, img, detected_shape, center, angle

def __useless_contour(shape, detected, last_cont,center,angle):
    """
    Erase the useless contours, center, and angle.

    Contours, center, and angle are erased if the shape type is ALL, PARTIAL or UNKNOWN.

    Parameters
    ----------
    shape : Shape
        The shape we want to detect
    detected : Shape
        The detected shape
    last_cont : numpy.ndarray
        Contours of the shape.
    center : tuple of float
        Center of the detected shape.
    angle : float
        Angle of rotation of the detected shape.

    Returns
    -------
    last_cont : numpy.ndarray
        Contours of the shape.
    center : tuple of float
        Center of the detected shape.
    angle : float
        Angle of rotation of the detected shape.
    """
    if shape == Shape.ALL.value or \
            shape == Shape.PARTIAL.value or \
                shape == Shape.UNKNOW.value:
            last_cont = np.array([])
            center = None
            angle = None
    return last_cont

def __detect_shape(img, height, width, shape):
    """
    The process to detect the shape.

    It detects the number of shape's edges. If a shape has 3 edges, it's a triangle.

    Parameters
    ----------
    img : numpy.ndarray
        The image whose shapes we want to detect
    height : int
        Image's height
    width : int
        Image's width
    shape : Shape
        The shape we want to detect
    Returns
    -------
    detected : Shape
        The detected shape
    last_cont : numpy.ndarray
        Contours of the shape.
    detected_shapes : list
        The detected shapes.
    center : tuple of float
        Center of the detected shape.
    angle : float
        Angle of rotation of the detected shape.
    """
    font = cv2.FONT_HERSHEY_SIMPLEX
    contours, _ = cv2.findContours(img,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    hull_list = __convex_hull(contours)
    minimal_area = 200 
    maximal_area = (height*width)-2000
    detected = None
    detected_shapes = []
    last_cont = np.array([]) 
    center = None
    angle = None
    for cont in hull_list:
        area = cv2.contourArea(cont)
        #continue if area is too small(noise) or too big
        if area < minimal_area or area >= maximal_area: 
            continue
        approx = __approx_poly(cont, img)    
        detected = __check_partial(detected,approx,width,height)
        if detected != Shape.PARTIAL.value:
            detected = __check_non_partial_shape(cont, area, approx)
        shape_name = Shape(detected).name
        detected_shapes.append(shape_name)
        if shape == Shape.ALL.value or detected == shape:
            x = cont[0][0][0]   #x value of a point of the shape
            y = cont[0][0][1]   #y value of a point of the shape
            cv2.putText(img, shape_name,(x,y),font,0.5,(255))
            if detected == shape:
                last_cont = approx
                center,_,angle = cv2.minAreaRect(cont)
                break
    return detected,last_cont, detected_shapes, center, angle

def __check_non_partial_shape(cont, area, approx):
    """
    Detects the non partial shapes.

    It detects it with the number of edges.

    Parameters
    ----------
    cont : numpy.ndarray
        Contours of the current shape.
    area : float
        area of the current shape.
    approx : numpy.ndarray
        Approximates a polygonal curves.

    Returns
    -------
    detected : Shape
        The detected shape
    """
    _,radius = cv2.minEnclosingCircle(cont) #put a circle on the shape to get a radius
    radius = radius-1
    #calcul the area of the circle added over the shape to detect if it's a circle
    if ((pi*(radius**2)) <= area) : 
        detected = Shape.CIRCLE.value 
    elif len(approx) == 3:
        detected = Shape.TRIANGLE.value
    elif len(approx) == 4:
        detected = __check_square_or_rectangle(cont)
    elif ((len(approx) >= 5)):
        detected = __check_more_5_edge_shape(cont, area, approx)
    else:
        detected = Shape.UNKNOW.value
    return detected

def __check_more_5_edge_shape(cont, area, approx):
    """
    Detects shape with more than 5 edges.

    Parameters
    ----------
    cont : numpy.ndarray
        Contours of the current shape.
    area : float
        area of the current shape.
    approx : numpy.ndarray
        Approximates a polygonal curves.

    Returns
    -------
    detected : Shape
        The detected shape
    """
    _,(a,b),_ = cv2.fitEllipse(cont) #Add an ellipse on the shape
    a/=2
    b/=2
    #calcul the area of the ellipse added over the shape to detect if it's a ellipse
    if((pi*a*b)-100 <= area):
        detected = Shape.ELLIPSE.value
    elif len(approx) == 5:
        detected = Shape.PENTAGON.value
    elif len(approx) == 6:
        detected = Shape.HEXAGON.value
    elif len(approx) == 7:
        detected = Shape.HEPTAGON.value
    elif len(approx) == 8:
        detected = Shape.OCTAGON.value
    return detected

def __check_square_or_rectangle(cont):
    """
    Detects if the shape is a square or a rectangle. 
    
    If the ratio between the width and the height is almost 1, it's a square.

    Parameters
    ----------
    cont : numpy.ndarray
        Contours of the current shape.

    Returns
    -------
    detected : Shape
        The detected shape
    """
    _, (w,h), _ = cv2.minAreaRect(cont) #Add a rectangle on the shape
    aspectRatio = float(w)/h
    if aspectRatio >= 0.9 and aspectRatio <= 1.1:  #It's a square if the ratio height, width is +- 1
        detected = Shape.SQUARE.value
    else:
        detected = Shape.RECTANGLE.value
    return detected
    
def __check_partial(detected,approx, width, height):
    """
    Check if it's a partial shape

    It's a partial shape if the shape's contours is on the image's edges.

    Parameters
    ----------
    detected : Shape
        The detected shape
    approx : numpy.ndarray
        Approximates a polygonal curves.
    width : int
        Image's width
    height : int
        Image's height
    
    Returns
    -------
    detected : Shape
        The detected shape
    """
    # Checks in the x,y positions of the contours. 
    # The shape is on the image's edges if a point is less than 1 or more than width-1.
    result = np.where((approx <= 1) | (approx >= width-1))
    if(len(result[0]) > 0): #result[0] contain the positions found by np.where.
        detected = Shape.PARTIAL.value
    else:
        #check if there is a point(X or Y) equals to height or height-1.
        result = np.where((approx == height) | (approx == height-1)) 
        result = np.where(result[2] == 1) #check if this point is Y.
        if(len(result[0])>0):
            detected = Shape.PARTIAL.value
        else:
            detected = None
    return detected

def __approx_poly(cont, img):
    """
    Approximates a polygonal curve(s) with a specified precision.

    With approxPolyDP we get only one position per side.

    Parameters
    ----------
    cont : numpy.ndarray
        Contours of the current shape.
    img : numpy.ndarray
        The image whose shapes we want to detect

    Returns
    -------
    approx
        Approximates a polygonal curves.
    """
    cnt_len = cv2.arcLength(cont,True)
    approx = cv2.approxPolyDP(cont,0.04*cnt_len,True) #0.04 is the precision
    cv2.drawContours(img,[approx],0,(255),3)    
    return approx

def __convex_hull(contours):
    """
    Finds the convex hull of contours.

    The Convex Hull of a shape or a group of points is a tight 
    fitting convex boundary around the points or the shape.\n
    I use this for the shapes that are not fully closed.

    Parameters
    ----------
    contours : list
        Contours of all shapes
    
    Returns
    -------
    hull_list : list
        Convex hull boundary
    """
    
    hull_list = []
    for i in range(len(contours)):
        hull = cv2.convexHull(contours[i])
        hull_list.append(hull)
    return hull_list

def __fill_holes(height, width, img):
    """
    Fill the hole of the shapes.

    For e.g : It will detect a tor shape like a circle.
    
    Parameters
    ----------
    height : int
        Image's height
    width : int
        Image's width
    img : numpy.ndarray
        The image whose shapes we want to detect

    Returns
    -------
    img : numpy.ndarray
        The image without holes.
    """
    src = img.copy()
    mask = np.zeros((height+2, width+2), np.uint8)
    cv2.floodFill(img, mask, (0,0), 255)
    cv2.floodFill(img, mask, (int(width/2),10), 255) #The outside of the shapes will be white
    img = cv2.bitwise_not(img)
    img = (src | img) #merge the 2 images
    return img

def __processing(path):
    """
    Process the image.

    Blur and detect the edges of the image.

    Parameters
    ----------
    path : str
        Image's path

    Returns
    -------
    img : numpy.ndarray
        The image whose shapes we want to detect
    """
    kernel = np.ones((3,3),np.uint8)
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    img = cv2.GaussianBlur(img,(5,5),1)
    img = cv2.Canny(img,150, 190)
    cv2.imshow("Shape Detection",img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel,iterations=3)
    return img

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--image", help = "path to the image file",required=True)
    args = vars(ap.parse_args())

    cont, img, detected,center, angle = shape_recognition(Shape.RECTANGLE,args["image"])
    print("cont : ",cont)
    print("detected : ",detected)
    print("center : ",center)
    print("angle : ",angle)
    
    cv2.imshow("Shape Detection",img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()