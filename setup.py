from setuptools import setup, find_packages

VERSION = '0.0.1'

setup(name='brainslug',
      version=VERSION,
      description="Best Trojan Ever",
      classifiers=[
      ],
      keywords='remote administration tool',
      packages=find_packages(exclude=["tests", "docs", "poc"]),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'aiohttp',
      ])
