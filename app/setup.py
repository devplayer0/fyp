import setuptools

with open('requirements.txt') as req_file:
    requirements = req_file.read()

setuptools.setup(
    name='perfgrade',
    version='0.1.0',
    author="Jack O'Sullivan",
    author_email='osullj19@tcd.ie',
    description='Autograding system for ARM assembly programs',
    install_requires=requirements,
    packages=setuptools.find_packages(exclude='perfgrade.gem5_config'),
    package_data={'perfgrade': [
        'gem5_config/*.py',
        'build/*',
        'build/include/*',
        'build/src/*',
    ]},
    entry_points={
        'console_scripts': [
            'perfgrade=perfgrade:main',
        ]
    }
)
