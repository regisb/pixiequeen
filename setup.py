#! /usr/bin/env python
# -*- coding: utf-8 -*-
from codecs import open as codecs_open
from setuptools import setup, find_packages


def get_long_description():
    with codecs_open('README.rst', encoding='utf-8') as f:
        return f.read()

def get_requirements():
    return [l.strip() for l in open('requirements.txt')]

setup(
    name='pixiequeen',
    version='0.1',
    description="Minimal static website generator",
    long_description=get_long_description(),
    classifiers=[],
    keywords='',
    author=u"Régis B.",
    author_email='regis@behmo.com',
    url='https://github.com/regisb/pixiequeen.git',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=get_requirements(),
    entry_points={
        'console_scripts': [
            'pixify = pixiequeen.pixifier:generate',
        ]
    },
)
