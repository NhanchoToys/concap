from setuptools import setup, find_packages
from os import path as os_path

import concap

this_directory = os_path.abspath(os_path.dirname(__file__))


# 读取文件内容
def read_file(filename):
    with open(os_path.join(this_directory, filename), encoding='utf-8') as f:
        long_description = f.read()
    return long_description


setup(
        name="concap",
        python_requires='>=3.7.0',
        version=concap.__version__,
        description="An interactive console implement.",
        long_description=read_file('README.md'),
        long_description_content_type="text/markdown",
        author="HivertMoZara",  # 以pypi用户名为准
        author_email="worldmozara@163.com",
        url="https://github.com/WorldMoZara/concap",
        packages=find_packages(),
        classifiers=[
            "Operating System :: OS Independent",
            "Programming Language :: Python :: 3",
            "Development Status :: 2 - Pre-Alpha",
            "License :: OSI Approved :: MIT License"
            ],
        )
