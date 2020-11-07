#!/usr/bin/python3

from distutils.core import setup

setup(name='getextensions',
      version='1.0',
      description='GNOME app to download and manage extensions',
      author='kaulfield',
      author_email='kaulfield@protonmail.com',
      url='https://github.com/ekistece/getextensions',
      packages=['getextensions', 'extensionmanager'],
      package_data={'getextensions': ['plugin.png']},
      include_package_data=True,
      data_files=[
        ('share/applications', ['data/org.getextensions.desktop'])],
      install_requires=[
          'requests', 'lxml',
      ],
)