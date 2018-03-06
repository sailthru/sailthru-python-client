from setuptools import setup, find_packages

setup(name='sailthru-client', 
    version='2.3.4',
    packages=find_packages(),
    description='Python client for Sailthru API',
    long_description=open('README.md').read(),
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Topic :: Utilities",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Natural Language :: English",
    ],
    install_requires=[
        'requests >= 2.6.0',
        'simplejson >= 3.0.7'
    ],
    keywords='sailthru api',
    author='Sailthru Inc.',
    author_email='support@sailthru.com',
    url='https://github.com/sailthru/sailthru-python-client',
    license='MIT License',
    include_package_data=True,
    zip_safe=True
)
