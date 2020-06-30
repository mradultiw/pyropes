import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyropes",
    version="1.2",
    author="Mradul Tiwari",
    author_email="complex.m15@gmail.com",
    description="An implementation of Rope Data Structure in Python3",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mradultiw/pyropes",
    project_urls={
    'Say Thanks!': 'https://www.paypal.me/mradultiw?locale.x=en_GB',
    'Source': 'https://github.com/mradultiw/pyropes',
    },
    packages=setuptools.find_packages(),
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        'Topic :: Utilities'
        
    ],
    python_requires='>=3.6',
)
