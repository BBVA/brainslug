from setuptools import setup, find_packages

VERSION = '0.0.2'

setup(name='brainslug',
      version=VERSION,
      description="Parasitic Computing Framework",
      long_description=open('README.rst', 'r').read(),
      classifiers=[
          "Development Status :: 3 - Alpha",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: Apache Software License",
          "Topic :: Internet",
          "Topic :: Security",
          "Topic :: Software Development :: Libraries :: Application Frameworks",
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
