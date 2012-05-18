from setuptools import setup, find_packages

version = '1.0.7'

setup(name='sailthru-client', 
        version=version,
        packages=find_packages(),
        description='Python client for Sailthru API',
        long_description=open('./README.md').read(),
        classifiers=[
            "License :: OSI Approved :: MIT License",
            "Topic :: Utilities",
            "Programming Language :: Python",
            "Operating System :: OS Independent",
            "Natural Language :: English",
            ],
        install_requires=[
            'requests'
        ],
        keywords='sailthru api',
        install_requires=['requests'],
        author='Prajwal Tuladhar',
        author_email='praj@sailthru.com',
        url='https://github.com/sailthru/sailthru-python-client',
        license='MIT License',
        packages=['sailthru'],
        include_package_data=True,
        zip_safe=True)
