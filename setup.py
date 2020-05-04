from setuptools import setup
from os import path
# io.open is needed for projects that support Python 2.7
# It ensures open() defaults to text mode with universal newlines,
# and accepts an argument to specify the text encoding
# Python 3 only projects can skip this import
from io import open

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()
setup(
    name='pshitt',
    version='1.0.1',
    description='Passwords of SSH Intruders Transferred to Text',
    long_description=long_description,
    long_description_content_type='text/x-rst',  # Optional (see note above)
    url='https://github.com/regit/pshitt',
    author='Eric Leblond',
    # author_email='pypa-dev@googlegroups.com',  # Optional
    classifiers=[  # Optional
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 5 - Production/Stable',

        # Indicate who your project is intended for
        'Intended Audience :: Information Technology',
        'Topic :: Security',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],

    keywords='ssh intrusion-detection',
    py_modules=['pshitt'],
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, <4',
    install_requires=['paramiko', 'python-daemon'],  # Optional
    package_data={  # Optional
        'test_rsa': ['test_rsa.key'],
    },
    entry_points={
        'console_scripts': [
            'pshitt=pshitt:main',
        ],
    },
    project_urls={
        'Bug Reports': 'https://github.com/regit/pshitt/issues',
        'Source': 'https://github.com/regit/pshitt/',
    },
)
