from setuptools import setup, find_packages

VERSION = '0.0.1'

setup(name='brainslug',
      version=VERSION,
      description="Parasitic Computing Framework",
      classifiers=[
      ],
      keywords='parasitic computing framework',
      packages=find_packages(exclude=["tests", "docs", "poc"]),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'aiohttp==3.5.4',
        'tinydb==3.12.2',
        'colorama==0.4.1',
        'aiohttp-cors==0.7.0'
      ],
      entry_points={
        'brainslug.ribosomes': [
            'powershell = brainslug.ribosomes.powershell:powershell'
        ]
      })
