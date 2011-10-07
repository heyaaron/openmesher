#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='openmesher',
      version='0.6.2',
      description='OpenMesher: Router OpenVPN p2p Mesh Link Generator',
      author='Aaron C. de Bruyn',
      author_email='aaron@heyaaron.com',
      url='https://github.com/darkpixel/openmesher',
      requires=['ipaddr', 'probstat', 'IPy', 'Yapsy', 'Jinja2'],
      packages=find_packages(),
      scripts=['openmesher.py'],
      install_requires=['distribute'],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: System Administrators',
          'Operating System :: POSIX',
          'Programming Language :: Python',
      ],  
      include_package_data=True,
      zip_safe=False,
)
