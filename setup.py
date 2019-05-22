#!/usr/bin/env python3

# Stephan Kuschel, Bjoern Senfftleben 2019

from setuptools import setup
import os
import os.path as osp
import versioneer


scripts = [osp.join('scripts',f) for f in os.listdir('scripts/')]
scripts = [f for f in scripts if osp.isfile(f)]
print('Found the following scripts: {}'.format(scripts))


setup(name='sqs_nqs_tools',
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      include_package_data=True,
      scripts=scripts,
      url='https://git.xfel.eu/gitlab/SQS/XFEL_SQS_NQS_Tools/',
      install_requires=['numpy>1.8','json'])
      
