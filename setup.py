# Author: Martin Babinsky <martbab@gmail.com>
# See LICENSE file for license

"""
Python package setup
"""

from distutils.core import setup


setup(
    author='Martin Babinsky',
    author_email='martbab@gmail.com',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        ("License :: OSI Approved :: GNU Lesser General Public License v3 or "
         "later (LGPLv3+)"),
        "Topic :: Utilities",
    ],
    description='A currency converter using latest rates fetched from fixer.io',
    entry_points={
        'console_scripts': [
            'currency-converter=currencyconv.cli:main'
        ]
    },
    install_requires=['pytest', 'forex-python'],
    license='GPLv3+',
    name='currency-converter',
    package_data={
        'test_data': 'tests/test_integration/data'
    },
    packages=['currencyconv', 'tests'],
    version='0.1',
)
