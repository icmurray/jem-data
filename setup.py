from distutils.core import setup

setup(
    name='JemData',
    version='0.1.0',
    author='Ian Murray',
    author_email='ian.c.murray@gmail.com',
    packages=['jem_data'],
    scripts=[],
    license='LICENSE.txt',
    long_description=open('README.md').read(),
    install_requires=[
        'Twisted==12.3.0',
        'pyasn1==0.1.4',
        'pycrypto==2.6',
        'pymodbus==1.1.0',
        'pymongo==2.4.2',
        'pyserial==2.6',
        'wsgiref==0.1.2',
        'zope.interface==4.0.3',
        'docopt==0.6.1',
    ],
)
