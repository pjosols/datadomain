from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='datadomain',
      version='0.1.0',
      description='Module for interacting with DataDomain backup appliance',
      long_description=readme(),
      url='https://github.com/pauljolsen/datadomain',
      author='Paul Olsen',
      author_email='paul@wholeshoot.com',
      license='MIT',
      packages=['datadomain'],
      install_requires=['requests', 'paramiko'],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Topic :: System :: Archiving :: Backup',
      ],
      keywords='flask django pymongo mongodb',
      include_package_data=True,
      zip_safe=False
      )
