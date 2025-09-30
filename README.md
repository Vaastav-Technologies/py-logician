# Logician

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/logician)
![PyPI - Types](https://img.shields.io/pypi/types/logician)
![GitHub License](https://img.shields.io/github/license/Vaastav-Technologies/py-logician)
[![🔧 test](https://github.com/Vaastav-Technologies/py-logician/actions/workflows/test.yml/badge.svg)](https://github.com/Vaastav-Technologies/py-logician/actions/workflows/test.yml)
[![💡 typecheck](https://github.com/Vaastav-Technologies/py-logician/actions/workflows/typecheck.yml/badge.svg)](https://github.com/Vaastav-Technologies/py-logician/actions/workflows/typecheck.yml)
[![🛠️ lint](https://github.com/Vaastav-Technologies/py-logician/actions/workflows/lint.yml/badge.svg)](https://github.com/Vaastav-Technologies/py-logician/actions/workflows/lint.yml)
[![📊 coverage](https://codecov.io/gh/Vaastav-Technologies/py-logician/branch/main/graph/badge.svg)](https://codecov.io/gh/Vaastav-Technologies/py-logician)
[![📤 Upload Python Package](https://github.com/Vaastav-Technologies/py-logician/actions/workflows/python-publish.yml/badge.svg)](https://github.com/Vaastav-Technologies/py-logician/actions/workflows/python-publish.yml)
![PyPI - Version](https://img.shields.io/pypi/v/logician)

---

**Fully typed, simple, intuitive, and pragmatic logger configurator for standard Python logging.**

`logician` is a lightweight logger-configurator that simplifies configuring Python's built-in `logging` module. It
supports logger setup using environment variables, CLI flags (`-v`, `-q`), and sensible defaults—all fully typed,
tested, and documented.

---

## 🚀 Features

* 🔧 **Minimal boilerplate** for structured logging
* 🌐 **Environment-variable driven configuration** (e.g. `LGCN_ALL_LOG=DEBUG`)
* ⚙️ **Verbosity-aware**: `-v`, `-vv`, `-q`, etc.
* 🎛️ **Different formats for different log levels**
* 🔌 Works seamlessly with standard loggers. More loggers are planned to be supported in the future.
* 🧪 **Fully type annotated** and well-tested via doctests
* 📚 **Extensive docstrings** with live examples
* 🗂️ **Per-module logging control**: associate specific environment variables with individual modules to fine‑tune log
  levels.

  For example:
  ```
  my_pkg.my_module    -> MY_MOD_ENV
  my.pkg.their_module -> TH_MOD_ENV
  their_pkg.kl.mod    -> KLO_ENV
  ```

  Users can then set environment variables to control log levels per module:
  ```bash
  MY_MOD_ENV=DEBUG KLO_ENV=TRACE python -m my_app
  ```
  This enables users to have fine-grained control over logging, and they can pin‑point issues just by
  enabling/disabling/verbosifying logging on a particular module of interest.
* 👀 **Logger-configurator Observability** Check what logger-configurator facilities are provided by the programs that use `logician`.

  For example:
  ```shell
  $ lgcn my-logician-using-command my-another-command cat
  ```
  ```terminaloutput
  # details about logger configurators of each command:
  {'my-logician-using-command': {'ro': {'env_list': ['IN_ENV', 'IN.ENV'],
                                       'level_list': [None, None],
                                       'level': 'Level 14',
                                       'propagate': False},
                                'ro.or': {'level': 'Level 14', 'propagate': False},
                                'r': {'env_list': ['ENV'],
                                      'level_list': [None],
                                      'level': 'Level 32',
                                      'propagate': False},
                                'r.c': {'env_list': ['ENV.C', 'ENV_C', 'ENV'],
                                        'level_list': [None, None, None],
                                        'level': 'Level 32',
                                        'propagate': False},
                                'c.r': {'level': 'Level 12',
                                        'verbosity': None,
                                        'quietness': None,
                                        'propagate': False}},
  'my-another-command cat': {'ro': {'env_list': ['IN_ENV', 'IN.ENV'],
                                    'level_list': [None, None],
                                    'level': 'Level 14',
                                    'propagate': False},
                             'ro.or': {'level': 'Level 14', 'propagate': False}},
  'cat': {}}    # no logger-configurator details for the `cat` command as it does not use logician.
  ```

---

## 📦 Installation

```bash
pip install logician
```

---

## 🧰 Quick Start

```python
from logician import get_direct_all_level_logger
import logging

_base_logger = logging.getLogger(__name__)
logger = get_direct_all_level_logger(_base_logger)
"""
The logician configured logger.
"""
logger.trace("🌀 Trace from logician.")
logger.debug("🐞 Debug from logician.")
logger.info("ℹ️ Info from logician.")
logger.success("✅ Success from logician.")
logger.notice("🔔 Notice from logician.")
logger.cmd("📺 My command's output (maybe captured stderr)", cmd_name="MY_CMD")
logger.warning("⚠️ Warning from logician.")
logger.error("❌ Error!")
logger.exception("🔥 Exception!")
logger.critical("🚨 Critical!")
logger.fatal("💀 Fatal!")
```

This sets up the root logger and all loggers derived from it with a sensible default formatter and log level.

---

## 🎁 Provided log levels out-of-the-box

Total eleven (🙀Dude, this many!🦾) log levels are provided out-of-the-box with room for more!.

These are listed in increasing order of criticality:

- TRACE
- DEBUG
- INFO
- SUCCESS
- NOTICE
- COMMAND
- WARNING
- ERROR 
- EXCEPTION 
  - (exception level is just a detailed error level.)
- CRITICAL
- FATAL 
  - (Yes, CRITICAL and FATAL are two different log levels.)

---

## 🔄 Environment Variable Configuration

### 🫶 Self-contained loggers within their own module

Modules can be configured to respond to certain env-vars which only correspond to their own logging, without affecting
other loggers or logger-configurators.

`logician` can read and set log levels from environment variables like:

```bash
MY_MODULE_LOG=DEBUG # module configured to respond to MY_MODULE_LOG env-var now logs on debug level
MY_SOME_MODULE_LOG=WARNING # other modules not affected by the configured module's logger
OTHER_MODULE_LOG=TRACE
```

These automatically control the logger levels without code changes.

You can also use the lower-level API directly, for e.g. the `APGEN` env-var is configured for the ap-generator app:

```python
from logician.stdlog.configurator import StdLoggerConfigurator
from logician.configurators.env import EnvListLC
import logging

base_logger = logging.getLogger('ap-generator')  # python std logger
logger = EnvListLC(["APGEN"], StdLoggerConfigurator(level=logging.INFO)).configure(base_logger)
```

One can have multiple env-vars set on the configurator with decreasing order of priority, for e.g.:

```python
import logging
from logician.stdlog.configurator import StdLoggerConfigurator
from logician.configurators.env import EnvListLC

base_logger = logging.getLogger('gp-generator')
logger = EnvListLC(["GPGEN", "GPGENLP"], StdLoggerConfigurator()).configure(base_logger)
"""
``GPGENLP`` has lower priority that ``GPGEN`` to the logger configurator.

if such is the setting
GPGEN=WARNING
GPGENLP=INFO

then WARNING level will be picked-up for logging.
"""
```

See `EnvListLC` in `logician.configurators.env` to learn more.

### 👑 One Env-var to rule all!

It can get quite detailed, verbose (and may I say, messy) to remember so many env-vars. Thus, `logician` also provides
env-var `LGCN_ALL_LOG` with the lowest priority which can set the log levels of all loggers:

```shell
# set logging level to INFO for all loggers in my-app
export LGCN_ALL_LOG=INFO
# run my app to see the magic!
python -m my-app
```

Since `LGCN_ALL_LOG` is the lowest priority env-var hence, other higher priority env-vars can take over the respective
configurations for their own module's logging if needed:

```shell
export LGCN_ALL_LOG=INFO

# all modules of my-app perform logging based on the LGCN_ALL_LOG env-vars's value (INFO) but the module configured to 
# respond to the ENV_VAR_FOR_MOD_OF_MY_INTRST env-var will only log on TRACE level. This will not affect logging of any 
# other module.
ENV_VAR_FOR_MOD_OF_MY_INTRST=TRACE my-app # command to run my-app (here run as a CLI script)
```

---

## 🗣️ CLI Verbosity Integration

Use `-v`, `-vv`, `-q`, `--quiet` flags from your CLI parser to dynamically set log levels:

```python
from argparse import ArgumentParser
from logician.stdlog.configurator import StdLoggerConfigurator, VQSepLoggerConfigurator
import logging

parser = ArgumentParser()
parser.add_argument("-v", "--verbose", action="count", default=0)
parser.add_argument("-q", "--quiet", action="count", default=0)
args = parser.parse_args()

lc = VQSepLoggerConfigurator(StdLoggerConfigurator(), verbosity=args.verbose, quietness=args.quiet)
logger = logging.getLogger(__name__)
logger = lc.configure(logger)
```

This configures the logger to reflect the verbosity or quietness of the CLI input.

---

## 🪄 Log Formatting by Log Level

Many-a-times it is the case that more refined (lower) log-levels need to output more (detailed) information. Hence,
`logician` maps more-detailed log-formats to lower log-levels. Different log levels can be mapped to different log
formats automatically which takes effects throughout all log levels.

> ⚠️ These format mappings currently assume use with Python's standard `logging` module. In the future, support may
> expand to other logging libraries or frameworks.

The default setup looks like this:

```python
WARN and up -> '%(levelname)s: %(message)s'
INFO -> '%(name)s: %(levelname)s: %(message)s'
DEBUG -> '%(name)s: %(levelname)s: [%(filename)s - %(funcName)10s() ]: %(message)s'
TRACE and lower -> '%(asctime)s: %(name)s: %(levelname)s: [%(filename)s:%(lineno)d - %(funcName)10s() ]: %(message)s'
```

You can override these or pass in your own formatting configuration.

---

## 🛠 Real-World Usage

### CLI Tools

* Have verbosity (v, vv, vvv) and quietness (q, qq, qqq) supported by the logger.

  ```shell
  # run my_tool with -qq cli args
  my_tool -qq
  ```
  ```python
  >>> import logging
  >>> from logician.stdlog.configurator import VQSepLoggerConfigurator, StdLoggerConfigurator
  
  >>> class Args:
  ...   "get args from CLI or argparse or click or whatever"
  ...   pass

  >>> args = Args()
  >>> args.verbose = "v"
  >>> args.quiet = None
  >>> lc = VQSepLoggerConfigurator(StdLoggerConfigurator(), verbosity=args.verbose, quietness=args.quiet)
  >>> _logger = logging.getLogger("my_tool")
  >>> logger = lc.configure(_logger)

  ```

### Environment Variables

* Support env-vars to configure logging levels (INFO, DEBUG, SUCCESS, ... etc)

  ```shell
  # run my-another-tool with env-var ENV1 supplying log level as ENV1=DEBUG
  ENV1=DEBUG my-another-tool
  ```
  ```python
  >>> import logging
  >>> from logician.configurators.env import LgcnEnvListLC
  >>> from logician.stdlog.configurator import StdLoggerConfigurator
  
  # get a logger configurator supporting ENV1 and ANO_ENV
  # now ENV1=DEBUG can be set to enable DEBUG level for the logger
  >>> lc = LgcnEnvListLC(["ENV1", "ANO_ENV"], StdLoggerConfigurator())
  >>> _logger = logging.getLogger("my-another-tool")
  >>> logger = lc.configure(_logger)
  
  ```

* Support env-vars to configure verbosity levels (v, vv, vvv, q, qq, qqq)

  ```shell
  # run my-another-tool with env-var ENV1 supplying log level as ENV1=q (sepcifying ERROR log leve;)
  ENV1=q my-another-tool
  ```
  ```python
  >>> import logging
  >>> from logician.configurators.env import LgcnEnvListLC
  >>> from logician.stdlog.configurator import StdLoggerConfigurator, VQCommLoggerConfigurator
  
  # get a logger configurator supporting ENV1 and ANO_ENV
  # now ENV1=vv can be set to enable DEBUG level for the logger
  >>> lc = LgcnEnvListLC(["ENV1", "ANO_ENV"], VQCommLoggerConfigurator(None, StdLoggerConfigurator()))
  >>> _logger = logging.getLogger("my-another-tool")
  >>> logger = lc.configure(_logger)
  
  ```

---

## 🧪 Testing & Typing

* ✅ 100% typed (compatible with MyPy)
* ✅ Doctests validated examples
* ✅ Deep pytests in `tests/`

---

## 📃 License

Apache License 2.0. See [LICENSE](./LICENSE) for full text.

---

## 🤝 Contributing

Contributions welcome!

```bash
git clone https://github.com/Vaastav-Technologies/py-logician.git
cd py-logician
```

[activate a venv](https://docs.python.org/3/library/venv.html), then run

```bash
pip install -e .[dev,test]  # install logician in local venv
pytest --cov  # run pytest with coverage
mypy -p logician  # check for static type safety
ruff check  # check for lints
ruff format # check for formats
```

Please write tests and add doctests for public facing APIs.

---

## 🔗 Links

* 📦 PyPI: [https://pypi.org/project/logician](https://pypi.org/project/logician)
* 🐙 GitHub: [https://github.com/Vaastav-Technologies/py-logician](https://github.com/Vaastav-Technologies/py-logician)
