from setuptools import setup, find_packages


def get_install_requires():
    return open("requirements.in").readlines()


setup(
    name="tagmunster",
    version="0.1.0",
    author="Rohan McGovern",
    author_email="rohan@mcgovern.id.au",
    packages=find_packages(exclude=["tests", "tests.*"]),
    url="https://github.com/rohanpm/tagmunster",
    license="GNU General Public License",
    description="GitHub action preparing release tags",
    install_requires=get_install_requires(),
    entry_points={
        "console_scripts": ["tagmunster=tagmunster.main:main"],
    },
)
