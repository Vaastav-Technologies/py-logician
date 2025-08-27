# logician

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

`logician` is a lightweight utility that simplifies configuring Python's built-in `logging` module. It supports logger setup using environment variables, CLI flags (`-v`, `-q`), and sensible defaults—all fully typed, tested, and documented.

---

## 🚀 Features

* 🔧 **Minimal boilerplate** for structured logging
* 🌐 **Environment-variable driven configuration** (e.g. `VT_ALL_LOG=DEBUG`)
* ⚙️ **Verbosity-aware**: `-v`, `-vv`, `-q`, etc.
* 🎛️ **Different formats for different log levels**
* 🔌 Works seamlessly with standard loggers and any logger name used by 3rd-party libraries (e.g., `"uvicorn"`, `"sqlalchemy"`) — assuming those libraries use standard Python logging
* 🧪 **Fully type annotated** and well-tested via doctests
* 📚 **Extensive docstrings** with live examples

> ⚠️ Note: `logician` assumes that external libraries like `uvicorn` and `sqlalchemy` use Python's standard `logging` module. If a library uses a custom or non-standard logging system, `logician` may not affect it.

---

## 📦 Installation

```bash
pip install logician
```

---

## 🧰 Quick Start

```python
from logician import configure

configure()

import logging
logger = logging.getLogger(__name__)
logger.info("Hello from logician!")
```

This sets up the root logger and all loggers derived from it with a sensible default formatter and log level.

---

## 🔄 Environment Variable Configuration

`logician` reads log levels from environment variables like:

```bash
LGCN_ALL_LOG=DEBUG
LGCN_SOME_MODULE_LOG=WARNING
```

These automatically control the logger levels without code changes.

You can change the prefix (default is `LGCN_`) via `env_prefix`:

```python
configure(env_prefix="APP_")
```

You can also use the lower-level API directly:

```python
from logician.std_log.configurator import StdLoggerConfigurator
from logician.configurators.env import LgcnEnvListLC
import logging

logger = logging.getLogger('ap-generator')
logger = LgcnEnvListLC(["APGEN"], StdLoggerConfigurator(level=logging.INFO)).configure(logger)
```

See `LgcnEnvListLC` in `logician.configurators.env` to learn more.

---

## 🗣️ CLI Verbosity Integration

Use `-v`, `-vv`, `-q`, `--quiet` flags from your CLI parser to dynamically set log levels:

```python
from argparse import ArgumentParser
from logician.std_log.configurator import StdLoggerConfigurator, VQSepLoggerConfigurator
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

Many-a-times it is the case that more refined (lower) log-levels need to output more (detailed) information. Hence, `logician` maps more-detailed log-formats to lower log-levels. Different log levels can be mapped to different log formats automatically which takes effects thoughout all log levels.

> ⚠️ These format mappings currently assume use with Python's standard `logging` module. In the future, support may expand to other logging libraries or frameworks.

The default setup looks like this:

```python
WARN and up -> '%(levelname)s: %(message)s'
INFO -> '%(name)s: %(levelname)s: %(message)s'
DEBUG -> '%(name)s: %(levelname)s: [%(filename)s - %(funcName)10s() ]: %(message)s'
TRACE and lower -> '%(asctime)s: %(name)s: %(levelname)s: [%(filename)s:%(lineno)d - %(funcName)10s() ]: %(message)s'
```

You can override these or pass in your own formatting configuration.

---

## 🛠️ Advanced Configuration

```python
from logician import configure

configure(
    logger_names=["sqlalchemy", "uvicorn"],
    level="INFO",
    env_prefix="MYAPP_",
    verbosity=1
)
```

### Keyword Arguments

| Param          | Type       | Description                                          |
| -------------- | ---------- | ---------------------------------------------------- |
| `logger_names` | list\[str] | Additional logger names to configure aside from root |
| `level`        | str / int  | Default log level (e.g., "INFO", 20)                 |
| `verbosity`    | int        | Verbosity count to decrease log level (`-v`)         |
| `quietness`    | int        | Quietness count to increase log level (`-q`)         |
| `env_prefix`   | str        | Prefix for reading env-based logger overrides        |

---

## 🧪 Example Doctest

All public APIs include doctests. Example:

```python
>>> from logician import derive_level
>>> derive_level(base="INFO", verbosity=1)
10
>>> derive_level(base="INFO", verbosity=0, quietness=1)
30
```

---

## 🛠 Real-World Usage

### FastAPI + Uvicorn + Environment config

```python
from logician import configure
configure(logger_names=["uvicorn", "sqlalchemy"], env_prefix="API_")
```

### CLI Tools

```python
from vt.utils.logging import VQSepLoggerConfigurator, StdLoggerConfigurator
import logging

lc = VQSepLoggerConfigurator(StdLoggerConfigurator(), verbosity=args.verbose, quietness=args.quiet)
logger = logging.getLogger("my_tool")
logger = lc.configure(logger)
```

---

## 🧪 Testing & Typing

* ✅ 100% typed (compatible with MyPy & Pyright)
* ✅ Doctests validate examples
* ✅ Poetry-managed project with tests in `tests/`

---

## 📃 License

Apache License 2.0. See `LICENSE` for full text.

---

## 🤝 Contributing

Contributions welcome!

```bash
git clone https://github.com/Vaastav-Technologies/py-logger.git
cd py-logger
poetry install
pytest
```

Please write tests and add doctests for public functions.

---

## 🔗 Links

* 📦 PyPI: [https://pypi.org/project/logician](https://pypi.org/project/logician)
* 🐙 GitHub: [https://github.com/Vaastav-Technologies/py-logger](https://github.com/Vaastav-Technologies/py-logger)
