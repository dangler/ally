from distutils.core import setup

setup(
    name='ally',
    version='0.3',
    packages=['ally'],
    url='',
    license='',
    author='jeremiahd',
    author_email='jeremiahd@slalom.com',
    description='assist in working with EC2 instances (connect, copy file, execute commands)',
    entry_points={
        'console_scripts': [
            'ally = ally.cli:cli',
        ],
    },
)
