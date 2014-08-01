#!/usr/bin/env python

from distutils.core import setup

setup(name='pixmap',
      version='0.1.0',
      description='Pixmap class for GIMP plugins',
      author='Lloyd Konneker',
      author_email='bootch@nc.rr.com',
      url='https://github.com/bootchk/pixmap',
      packages=['pixmap', 
                'pixmap.bounds',
                'pixmap.coord',
                'pixmap.pixelelID',
                'pixmap.pixmap',
                'pixmap.pixmapMask',
                ],
     )