from setuptools import setup
from codecs import open
from os import path


current_path = path.abspath(path.dirname(__file__))


with open(path.join(current_path, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='beval',

    version='1.0.4',

    description='boolean expression evaluator',

    long_description=long_description,

    url='https://github.com/hyw208/beval',

    license='Apache License, Version 2.0',

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ],

    keywords='boolean expression evaluator util',

    author='hyw208',

    author_email='hyw208@gmail.com',

    test_suite='nose.collector',

    tests_require=['nose'],

    install_requires=[],

    packages=['beval'],

    zip_safe=False,

)