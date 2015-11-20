# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


setup(
    name='tc_video',
    version='0.1.0',
    url='http://github.com/thumbor_community/video',
    license='MIT',
    author='Thumbor Community',
    description='Thumbor community video extensions',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=[
        'thumbor>=5.0.6',
    ],
    extras_require={
        'tests': [
            'pyvows',
            'coverage',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
