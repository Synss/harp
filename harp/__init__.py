"""
The Core (:mod:`harp`) package is the root namespace of the Harp framework.

It mostly contains a reference to the :class:`Config` class, because it's the only object you need to start using Harp
using the python API (you don't *need* to use this API, configuration files should be enough for most use cases, but
if you want to, this is the starting point).

For convenience, the :func:`run` function is also available, which is a simple way to start the default server
implementation for your configuration object.

Example usage:

.. code-block:: python

    from harp import Config, run

    config = Config()
    config.add_defaults()

    if __name__ == "__main__":
        run(config)

You can find more information about how configuration works in the :mod:`harp.config` module.

Contents
--------

"""

import os
from subprocess import check_output

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# last release
__title__ = "Core"
__version__ = "0.4.0"
__revision__ = __version__  # we can't commit the not yet known revision

# override with version.txt if available (after docker build for example)
if os.path.exists(os.path.join(ROOT_DIR, "version.txt")):
    with open(os.path.join(ROOT_DIR, "version.txt")) as f:
        __version__ = f.read().strip()

# override with current development version/revision if available (disabled in CI, for docs)
if not os.environ.get("CI", False) and os.path.exists(os.path.join(ROOT_DIR, ".git")):
    __revision__ = check_output(["git", "rev-parse", "HEAD"], cwd=ROOT_DIR).decode("utf-8").strip()
    try:
        __version__ = (
            check_output(["git", "describe", "--tags", "--always", "--dirty"], cwd=ROOT_DIR).decode("utf-8").strip()
        )
    except Exception:
        __version__ = __revision__[:7]

from ._logging import get_logger  # noqa: E402, isort: skip
from harp.config import Config  # noqa: E402, isort: skip


def run(config: Config):
    """
    Run the default server using provided configuration.

    :param config: Config
    :return:
    """
    import asyncio
    import sys

    from harp.config.adapters.hypercorn import HypercornAdapter
    from harp.config.factories.kernel_factory import KernelFactory

    config.read_env(sys.argv[1:])
    factory = KernelFactory(config)
    server = HypercornAdapter(factory)
    asyncio.run(server.serve())


__all__ = [
    "Config",
    "ROOT_DIR",
    "__revision__",
    "__version__",
    "get_logger",
    "run",
]
