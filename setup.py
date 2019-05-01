#!/usr/bin/env python3

# Stephan Kuschel, 2019

from setuptools import setup
import os
import os.path as osp
import versioneer


scripts = [osp.join('scripts',f) for f in os.listdir('scripts/')]
scripts = [f for f in scripts if osp.isfile(f)]
print('Found the following scripts: {}'.format(scripts))


setup(name='xfelmay2019',
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      include_package_data=True,
      scripts=scripts,
      url='https://github.com/skuschel/XFELMay2019',
      install_requires=['numpy>1.8'])
      
