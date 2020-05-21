# Shape processing

Shape_processing is a package to get the size of a specific shape with an IFM O3X101 camera.


| Folder                                | Content                                                                               |
|---------------------------------------|---------------------------------------------------------------------------------------|
| docs/                                 | Html documentation                                                                    |
| lib/                                  | Libraries                                                                             |
| shape_processing/                     | Code                                                                                  |
| shape_processing/Camera.py            | Create camera with IP address + take picture                                          |
| shape_processing/Shape.py             | Define the different types of shapes                                                  |
| shape_processing/shape_recognition.py | Detects different types of shapes on an image. Give its position, center and angle.   |
| shape_processing/shape_size.py        | Get the height, width and length of the shape.                                        |
| shape_processing/ur3.py               | To grab the object with a UR3 robot                                                   |


## Installation

### Explanations

First, our computer has to be up to date.

Next, we have to install all the dependencies of the ifm library. 

Then, we clone  the libraries to be installed. pybind11 is also a dependency. But we have to build it by hand.

After, we build the pybind11 dependency.

Finally, we install the requirements who will install ifm3dpy library.

### Commands
```
sudo apt update && sudo apt upgrade
sudo apt  install -y libboost-all-dev git jq libcurl4-openssl-dev \
                              libgtest-dev libgoogle-glog-dev  \
                              libxmlrpc-c++8-dev libopencv-dev \
                              libpcl-dev libproj-dev \
                              build-essential coreutils cmake python3-pip
cd lib/
git clone https://github.com/ifm/ifm3d.git
git clone https://github.com/pybind/pybind11
cd pybind11
mkdir build
cd build
cmake -DPYBIND11_TEST=OFF ..
make
sudo make install
cd ../../..
pip3 install -r requirements.txt
```

## How to use it ?

### Modify the detected shape

In main.py change the shape (RECTANGLE) to the desired one.

See in the html documentation in "Shape" to have all accepted shapes.


### Execute the code
Via the terminal.

```
python3 main.py
```

It will output a picture with the detected shape.

