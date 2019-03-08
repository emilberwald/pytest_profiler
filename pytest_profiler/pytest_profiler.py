import io
import multiprocessing
import pathlib
from urllib.parse import quote_plus

import pytest
import yappi

semaphore = multiprocessing.Semaphore(1)


class PytestProfiler:
    def __init__(self, outdir):
        self.func_stats_summary = io.StringIO()
        self.outdir = pathlib.Path(outdir)

    def pytest_sessionstart(self, session):
        pass

    def pytest_sessionfinish(self):
        yappi.clear_stats()
        pass

    def pytest_terminal_summary(self, terminalreporter):
        terminalreporter.write("\n" + "=" * 80 + "\n")
        terminalreporter.write(str(self.func_stats_summary.getvalue()))
        terminalreporter.write("\n" + "=" * 80 + "\n")

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_call(self, item):
        yappi.start(builtins=False, profile_threads=True)
        yield
        yappi.stop()

        func_stats = yappi.get_func_stats()
        self.outdir.mkdir(parents=True, exist_ok=True)
        path = (
            self.outdir / pathlib.Path(quote_plus(item.name, safe="/[],._") + ".prof")
        ).absolute()
        func_stats.save(str(path), type="PSTAT")
        self.func_stats_summary.write("\n" + "-" * 80 + "\n")
        self.func_stats_summary.write(
            f"function statistics\n{item.name}\n{str(path)}\n"
        )
        func_stats.sort("ttot").print_all(self.func_stats_summary)
        self.func_stats_summary.write("\n" + "-" * 80 + "\n")
        func_stats.clear()


def pytest_addoption(parser):
    group = parser.getgroup("Profiling")
    group.addoption(
        "--profile",
        action="store_true",
        default=False,
        help="generate profiling information",
    )
    group.addoption(
        "--profile-outdir",
        default="prof",
        help="output directory (places pstat .prof files here)",
    )


def pytest_configure(config):
    with semaphore:
        profiling_enabled = bool(config.getoption("--profile"))
        if profiling_enabled:
            if not config.pluginmanager.is_registered("pytest_profiler"):
                config.pluginmanager.register(
                    PytestProfiler(config.getoption("--profile-outdir"))
                )
