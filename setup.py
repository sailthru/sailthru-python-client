from setuptools import setup

version = '1.0.2'

setup(name='sailthru-client', 
        version=version,
        description='Python client for Sailthru API',
        long_description=open('./README.md').read(),
        classifiers=[
            "License :: OSI Approved :: MIT License",
            "Topic :: Utilities",
            "Programming Language :: Python",
            "Operating System :: OS Independent",
            "Natural Language :: English",
            ],
        keywords='sailthru api',
        author='Prajwal Tuladhar',
        author_email='praj@sailthru.com',
        url='https://github.com/sailthru/sailthru-python-client',
        license='MIT License',
        packages=['sailthru'],
        include_package_data=True,
        zip_safe=True)
