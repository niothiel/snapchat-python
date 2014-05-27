from setuptools import setup

setup(name='snapchat',
      version='0.1',
      description='Implementation of the Snapchat protocol in Python',
      url='https://github.com/itsnauman/snapchat-python',
      author='Nauman Ahmad',
      author_email='nauman-ahmad@outlook.com',
      license='MIT',
      packages=['snapchat'],
      install_requires=[
          'requests==2.0.1',
          'pycrypto==2.6.1'
      ],
      zip_safe=False)
