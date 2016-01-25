from setuptools import setup, find_packages

with open('README.rst', 'r') as infile:
    read_me = infile.read()


setup(
    name='anime-tools',
    version='0.1.0',
    description='scripts for various common anime content-related tasks',
    long_description=read_me,
    author='Ofek Lev',
    author_email='ofekmeister@gmail.com',
    maintainer='Ofek Lev',
    maintainer_email='ofekmeister@gmail.com',
    url='https://github.com/Ofekmeister/pymedia',
    license='MIT',
    platforms=None,

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    install_requires=['chardet', 'pyperclip'],
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'subshift = anime-tools.subshift:main',
            'epirename = anime-tools.subrename:main',
        ],
    },
)
