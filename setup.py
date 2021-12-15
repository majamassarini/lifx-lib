from os import path
from setuptools import setup, find_packages

long_description = ""
with open(path.join(".", 'README.md'), encoding='utf-8') as f:
      long_description = f.read()

setup(name="lifx-lib",
      version="0.9.1",
      description="A python3 library able to encode/decode Lifx (lan) messages",
      url="https://github.com/majamassarini/lifx-lib",
      long_description=long_description,
      long_description_content_type='text/markdown',
      author="Maja Massarini",
      author_email="maja.massarini@gmail.com",
      license="MIT",
      classifiers=[
            "Development Status :: 3 - Alpha",
            "License :: OSI Approved :: MIT License",
            "Operating System :: POSIX :: Linux",
            "Programming Language :: Python :: 3.8",
            "Topic :: Communications",
            "Intended Audience :: Developers",
      ],
      packages=find_packages(exclude=[]),
      include_package_data=True,
      )


