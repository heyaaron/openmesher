#!/usr/bin/env python

from distutils.core import setup

setup(name='openmesher',
      version='0.4',
      description='OpenMesher: Router OpenVPN p2p Mesh Link Generator',
      author='Aaron C. de Bruyn',
      author_email='aaron@heyaaron.com',
      url='http://github.com/darkpixel/openmesher',
      requires=['ipaddr', 'probstat', 'IPy'],
)
