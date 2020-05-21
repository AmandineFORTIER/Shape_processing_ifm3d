from tkinter import *
import math
import numpy as np
import socket

HOST = "192.168.1.60"
PORT = 30001

class GUI_Positions:
    """
        GUI Position class is a GUI to declare the position of the robot on the image.
        It will save the robot position at the top left, top right, 
        bottom left and bottom right of the camera's view.
        """
    def __init__(self):
        """
        Initialise the GUI.
        """
        self.window = Tk()
        self.frame = Frame(self.window)
        self.pos_value={}
        self.__create_widgets()
        self.frame.pack(expand=YES)

    @property
    def get_pos(self):
        """
        Get the robot position.

        Returns
        -------
        pos_value : dict
            A dictionnary that contains the positions. e.g 'Top Left': ['116', '-319']
        """
        return self.pos_value
    
    def __create_widgets(self):
        """
        Create widgets.
        """
        self.__create_pos_box("Top Left").pack()
        self.__create_pos_box("Top Right").pack()
        self.__create_pos_box("Bottom Left").pack()
        self.__create_pos_box("Bottom Right").pack()
        val = self.__create_pos(self.frame,"z : ",-50,500)
        self.pos_value["Z"] = [val]
        Button(self.frame,text="Validate",command=self.window.quit,width=15).pack()

    def __create_pos_box(self,title):
        """
        Create widget for each positions.


        Parameters
        ----------
        title : str
            Title's widget.

        Returns
        -------
        frame_pos : tkinter.Frame
            The frame that contains the label and 2 box for x and y position.
        """
        frame_pos = Frame(self.frame)
        label_title = Label(frame_pos,text=title)
        label_title.pack()
        x,y = self.__create_xy(frame_pos)
        self.pos_value[title]= [x,y]
        return frame_pos

    def __create_xy(self,frame):
        """
        Create 2 box. One for x another for y.
        Spinbox can have a value from -540 to 540.
        To get it I moved the robot as far as possible and I took the values.

        Parameters
        ----------
        frame : tkinter.Frame
            Frame to put the widget.

        Returns
        -------
        x : tkinter.Spinbox
            Spinbox with the selected x value
        y : tkinter.Spinbox
            Spinbox with the selected y value
        """
        frame_xy = Frame(frame)
        x = self.__create_pos(frame_xy,"x : ",-540,540)
        y = self.__create_pos(frame_xy,"y : ",-540,540)
        frame_xy.pack()
        return x, y

    def __create_pos(self,frame,text,minV,maxV):
        """
        Create a spinbox with a minimal and maximale value.

        Parameters
        ----------
        frame : tkinter.Frame
            Frame to put the widget.
        text : str
            Title of the box
        minV : int
            Minimal value for a position.
        maxV : int
            Maximal value for a position.

        Returns
        -------
        num : tkinter.Spinbox
            Spinbox. The value is in mm.
        """
        frame_entry_pos = Frame(frame)
        lab = Label(frame_entry_pos,text=text)
        num = Spinbox(frame_entry_pos,from_=minV, to=maxV)
        num.delete(0,END)
        num.insert(0,0)
        lab.grid(row = 0, column = 0)
        num.grid(row = 0, column = 1)
        Label(frame_entry_pos,text=" mm").grid(row = 0, column = 2)
        frame_entry_pos.pack()

        return num 

def get_object(dic, img_width, img_height, center,z,angle):
    """
    Move the UR3 robot to get the object.

    Parameters
    ----------
    dic : dict
        Dictionnary of positions.
    img_width : int
        Width size of the image. In pixel.
    img_height : int
        Height size of the image. In pixel.
    center : list
        Object's center. In pixel.
    z : float
        Object's height.
    angle : float
        Angle of rotation of the object.
    """
    x, y = __calcul_positions(dic,img_width,img_height,center)
    __goto_object(dic,x,y,z,angle)

def __spin_to_val(arr):
    """
    Modify the array of spinbox to get an array of spinboxe's value.

    Parameters
    ----------
    arr : list
        List of spinbox.

    Returns
    -------
    arr : list
        List of spinbox's value.
    """
    for a in range(len(arr)):
        arr[a] = arr[a].get()
    return arr

def __calcul_positions(dic_pos,img_width,img_height,center):
    """
    Get X and Y distance of the center of the object from the top left.

    The camera can be on the front, left, right, or back of the robot. So the delta x and y will be sometimes swapped or inverted.
    x become -x if the top left x is positive. same for y. if x and y of top left have the same sign, we swap x and y.

    Parameters
    ----------
    dic_pos : dict
        Dictionnary of positions.
    img_width : int
        Width size of the image. In pixel.
    img_height : int
        Height size of the image. In pixel.
    center : list
        Object's center. In pixel.

    Returns
    -------
    x : float
        Distance from top left X to the center X position.
    y : float
        Distance from top left Y to the center Y position.
    """
    try:
        pixel_size = __get_pixel_metric_value(dic_pos, img_width, img_height)
    except ValueError as e:
        print(e)
        return 0,0
    x = center[0]*pixel_size
    y = center[1]*pixel_size
    x1,y1 = dic_pos.get("Top Left")
    x = -x if(int(x1) >0) else x
    y = -y if(int(y1) >0) else y
    if (int(x1) >0 and int(y1) >0) or (int(x1) <0 and int(y1)<0):
        return y, x
    return x, y

def __get_pixel_metric_value(dic_pos, img_width, img_height):
    """
    Get the pixel metric value (mm). From the camera to the robot.
    
    Parameters
    ----------
    dic_pos : dict
        Dictionnary of positions.
    img_width : int
        Width size of the image. In pixel.
    img_height : int
        Height size of the image. In pixel.

    Returns
    -------
    pixel_size : float
        The size of a pixel in mm for the robot.
    """
    x1,y1 = dic_pos.get("Top Left")
    x2,y2 = dic_pos.get("Top Right")
    width_metric = math.sqrt((int(x2) - int(x1))**2 + (int(y2) - int(y1))**2) 
    x3,y3 = dic_pos.get("Bottom Left")
    height_metric = math.sqrt((int(x3) - int(x1))**2 + (int(y3) - int(y1))**2) 
    pixel_size = height_metric/img_height
    pixel_size2 = width_metric/img_width
    if pixel_size < pixel_size2-0.01 or pixel_size > pixel_size2+0.01:
        raise ValueError("The positions don't match the image. There's a bad ratio.") #It has to be the same ratio than the camera
    return pixel_size

def __goto_object(dic, x, y, z, angle):
    """
    Get the pixel metric value (mm). From the camera to the robot.
    
    Parameters
    ----------
    dic : dict
        Dictionnary of positions.
    x : float
        Delta X. Distance from Top left X and center X.
    y : float
        Delta y. Distance from Top left y and center y.
    z : float
        The object's height.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    output = __ur3_init(dic)        
    output +=__ur3_move(0,0,z+200,angle, False) #open grip and go up
    output +=__ur3_move(x,y,z+100,angle, False) #go to the top of the object
    output +=__ur3_move(0,0,z,angle, False) 
    output +=__ur3_move(0,0,z,angle, True)    #close the grip to get the object
    output +=__ur3_move(0,0,z+200,angle, True)
    output +="""end\n"""
    s.sendall(output.encode('utf-8'))
    s.close()

def __ur3_init(dic):
    """
    Initialise the robot. Go to home position then to Top Left position.
    
    Parameters
    ----------
    dic : dict
        Dictionnary of positions.
    
    Returns
    -------
    output : str
        The message to send to the robot.
    """
    x = int(dic.get("Top Left")[0])
    y = int(dic.get("Top Left")[1])
    output = """def urProf():\n
    movej([0,-1.5708,0,-1.5708,0,0],a=1,v=1)\n
    global init_x = """+str(x/1000)+"""\n
    global init_y = """+str(y/1000)+"""\n
    movej(p[init_x,init_y,0.15728,0.0001,-3.166,-0.04],a=1,v=1)\n"""
    return output

def __ur3_move(dx, dy, z, angle, close_grip):
    """
    Move the robot.
    
    Parameters
    ----------
    dx : int
        Delta X.
    dy : int
        Delta Y.
    z : int
        Height.
    angle : float
        Angle of rotation of the object.
    close_grip : bool
        True if we want to close the grip.
    
    Returns
    -------
    output : str
        The message to send to the robot.
    """
    output = """global x="""+str(dx/1000)+"""\n
    global y="""+str(dy/1000)+"""\n
    global z="""+str(z/1000)+"""\n
    global angle="""+str(angle)+"""\n
    angle=d2r(angle)\n
    global pos=get_actual_tcp_pose()\n
    pos[0]=pos[0]+x\n
    pos[1]=pos[1]+y\n
    pos[2]=z\n
    pos[3]=angle\n
    set_tool_digital_out(0,"""+str(close_grip)+""")\n
    movel(pos,a=1,v=1)\n"""
    return output

if __name__=="__main__":
    """
    Main program. If we put argument, the GUI will be displayed to specify the positions.
    If no argument are passed, it will use a predefine dictionnary of positions.
    """
    if len(sys.argv) > 1:
        app = GUI_Positions()
        app.window.mainloop()
        
        dic = app.get_pos
        for pos in dic.values():
            pos = __spin_to_val(pos)
    else:
        left = {'Top Left': ['116', '-319'], 'Top Right': ['34', '-319'], 'Bottom Left': ['116', '-256'], 'Bottom Right': ['34', '-256'], 'Z': ['10']}
        back = {'Top Left': ['312', '80'], 'Top Right': ['312', '-85'], 'Bottom Left': ['187', '80'], 'Bottom Right': ['187', '-85'], 'Z': ['10']}
        dic = back
    angle = -51.842769622802734
    img_width = 224
    img_height = 172
    z=120
    center = [118.3233413696289, 105.8612060546875]
    get_object()
   
