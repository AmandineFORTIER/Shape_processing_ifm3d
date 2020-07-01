import ifm3dpy
import sys

class Camera:
    def __init__(self, ip=ifm3dpy.DEFAULT_IP):
        """
        Create the camera object.

        With RDIS and AMP to get Distance or Amplitude image.
        
        Parameters
        ----------
        ip : str
            Camera's IP.
        """
        self.cam = ifm3dpy.Camera(ip)
        try:
            self.fg = ifm3dpy.FrameGrabber(self.cam, ifm3dpy.IMG_RDIS |ifm3dpy.IMG_AMP)
        except RuntimeError as e:
            print(e)
            sys.exit() 
        self.im = ifm3dpy.ImageBuffer()

    def get_image(self):
        """
        Get the image from the camera

        Takes a picture.

        Returns
        -------
        im : ifm3dpy.ImageBuffer
            The picture.
        
        Raises
        ------
        RuntimeError
            If it can not get a frame.
        """
        nb_try = 5
        for i in range(nb_try):
            if self.fg.wait_for_frame(self.im, 1000):
                break
        if(i == nb_try-1):
            raise RuntimeError('Timeout waiting for camera!')
        return self.im
