#!/usr/bin/python3

from distutils.core import setup

setup(name='getextensions',
      version='1.0',
      description='GNOME app to download and manage extensions',
      author='ekistece',
      url='https://github.com/ekistece/getextensions',
      packages=['getextensions', 'extensionmanager'],
      package_data={'getextensions': ['plugin.png']},
      include_package_data=True,
      data_files=[
        ('share/applications', ['data/org.getextensions.desktop']),
        ('share/icons/hicolor/128x128/apps', ['data/getextensions.svg'])],
      install_requires=[
          'requests', 'lxml',
      ],
)
