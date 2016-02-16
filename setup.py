from setuptools import setup

setup(name='mdc_api',
      version='1.0.0',
      description='REST interface library for mbed Device Connector (connector.mbed.com)',
      url='http://github.com/armmbed/mdc-api-python',
      author='ARM mbed',
      author_email='support@mbed.com',
      license='Apache 2.0',
      packages=['mdc_api'],
      keywords='ARM mbed connector device mDC mDS ARMmbed',
      install_requires=[
          'requests',
      ],
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Utilities',
        'Intended Audience :: Developers',
      ],
      test_suite='nose.collector',
      tests_require=['nose', 'nose-cover3'],
      #entry_points={
      #    'console_scripts': ['funniest-joke=funniest.command_line:main'],
      #},
      zip_safe=False)