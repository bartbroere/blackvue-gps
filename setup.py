from setuptools import setup

with open('README.md', 'r') as readme:
    readme = "".join(readme.readlines())

with open('requirements.in', 'r') as requirements:
    dependencies = [dependency.split('#')[0].replace('\n', '').replace(' ', '')
                    for dependency in requirements.readlines() if
                    dependency[0] != '#']

setup(
    name='blackvue_gps',
    version='2018.7.14',
    url='https://github.com/bartbroere/blackvue-gps/',
    author='Bart Broere',
    author_email='maiil@bartbroere.eu',
    license='MIT License',
    description="Parse GPS records created by BlackVue Dashcams.",
    keywords='blackvue gps dashcam nmea parse parser',
    long_description=readme,
    py_modules=['blackvue_gps'],
    install_requires=dependencies,

    classifiers=(
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Utilities',
    )
)
