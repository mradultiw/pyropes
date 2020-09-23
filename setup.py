import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyropes",
    version="1.4",
    author="Mradul Tiwari",
    author_email="complex.m15@gmail.com",
    description="An implementation of Height Balanced Threaded Rope Data Structure in Python3",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mradultiw/pyropes",
    project_urls={
    'Source': 'https://github.com/mradultiw/pyropes',
    },
    packages=setuptools.find_packages(),
    classifiers=[
        "Intended Audience :: Education",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        'Topic :: Education',
        'Topic :: Utilities',

    ],
    python_requires='>=3.6',
)
