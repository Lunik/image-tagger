#!/usr/bin/env python
# pylint: disable=missing-docstring
import os
from setuptools import setup, find_packages


def get_version():
    """Get version from __init__.py file."""
    filename = os.path.join(
        os.path.dirname(__file__), "lib", "imagetagger", "__init__.py"
    )
    with open(filename, encoding="UTF-8") as file:
        for line in file:
            if line.startswith("__version__"):
                return eval(line.split("=")[-1])  # pylint: disable=eval-used

    raise ValueError(f"No __version__ defined in {filename}")


setup(
    name="imagetagger",
    version=get_version(),
    description="Add exif tags to images using AI",
    long_description=open(  # pylint: disable=consider-using-with
        "README.md", encoding="UTF-8"
    ).read(),
    long_description_content_type="text/markdown",
    author="Guillaume MARTINEZ",
    author_email="lunik@tiwabbit.fr",
    maintainer="Guillaume MARTINEZ",
    maintainer_email="lunik@tiwabbit.fr",
    url="https://github.com/Lunik/image-tagger",
    download_url="https://github.com/Lunik/image-tagger",
    license_files=("LICENSE",),
    package_dir={"": "lib"},
    packages=find_packages(where="lib"),
    include_package_data=True,
    entry_points={
        "console_scripts": ["image-tagger = imagetagger:main"],
    },
    python_requires=">=3.8.0",
    install_requires=[
        "ollama==0.2.*",
        "rich==13.*",
        "exif==1.*",
        "Pillow==10.*",
    ],
    extras_require={
        "dev": [
            "pylint",
            "black",
            "build",
            "wheel",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Information Technology",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Graphics :: Editors",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
