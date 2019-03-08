import setuptools

setuptools.setup(
    name="pytest_profiler",
    packages=["pytest_profiler"],
    # the following makes a plugin available to pytest
    entry_points={"pytest11": ["pytest_profiler = pytest_profiler.pytest_profiler"]},
    # custom PyPI classifier for pytest plugins
    classifiers=["Framework :: Pytest"],
    install_requires=["yappi", "pytest"]
)
