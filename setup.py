from setuptools import setup, find_packages

setup(name='sailthru-client', 
    version='2.1.4',
    packages=find_packages(),
    description='Python client for Sailthru API',
    long_description=open('README.md').read(),
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Topic :: Utilities",
        "Programming Language :: Python",
        "Operating System :: OS Independent",
        "Natural Language :: English",
    ],
    install_requires=[
        'requests >= 0.12.0',
        'simplejson >= 2.0'
    ],
    keywords='sailthru api',
    author='Prajwal Tuladhar',
    author_email='praj@sailthru.com',
    url='https://github.com/sailthru/sailthru-python-client',
    license='MIT License',
    include_package_data=True,
    zip_safe=True
)
