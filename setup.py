from distutils.core import setup

setup(
    name='ally',
    version='0.1',
    packages=['ally'],
    url='',
    license='',
    author='jeremiahd',
    author_email='jeremiahd@slalom.com',
    description='connect to ec2 instances',
    entry_points={
        'console_scripts': [
            'ally = ally.cli:cli',
        ],
    },
)
