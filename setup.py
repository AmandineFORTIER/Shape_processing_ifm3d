from setuptools import setup

setup(name="Shape processing",
      version="1.0",
      author="Amandine FORTIER",
      description="Use of an IFM3X101 camera to recognize different shapes and calculate their sizes. The object of the desired shape will be grabbed by an UR3 robot",
      packages=["shape_processing_ifm_ur3"],
      zip_safe=False)