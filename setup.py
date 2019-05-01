#!/usr/bin/env python3

# Stephan Kuschel, 2019

from setuptools import setup

import versioneer

setup(name='xfelmay2019',
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      include_package_data=True,
      url='https://github.com/skuschel/XFELMay2019',
      install_requires=['numpy>1.8'])
      
