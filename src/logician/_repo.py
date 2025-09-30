#!/usr/bin/env python3
# coding=utf-8

"""
A repo implementation for observability of logger configurators.
"""

import abc
import configparser
import json
import os
import tempfile
import tomllib
from abc import abstractmethod
from collections import defaultdict
from pathlib import Path
from typing import Protocol, Any, override

from logician.constants import LGCN_INFO_FP_ENV_VAR


class Persister[DS](Protocol):
    """
    A persister that can persist in-mem data of the ``DS`` data-structure format.

    ``DS`` - data-structure that this persister works with.
    """

    @abstractmethod
    def init(self):
        """
        Initialise the persistence storage.
        """

    @abstractmethod
    def commit(self, ds: DS):
        """
        Write ``ds`` to the persistent storage.

        :param ds: data-structure carrying writable payload.
        """
        ...

    @abstractmethod
    def reload(self) -> DS:
        """
        Read from persistent storage.

        :return: the read payload.
        """


class PathProvider(Protocol):
    @abstractmethod
    def get_path(self) -> Path: ...


class HasPathProvider(Protocol):
    @property
    @abstractmethod
    def path_provider(self) -> PathProvider: ...


class HandlerPathProvider(PathProvider, HasPathProvider, Protocol):
    pass


class FilePathProvider(HandlerPathProvider):
    def __init__(self, path_provider: "FilePathProvider"):
        self._path_provider = path_provider

    @abstractmethod
    def _get_file_path(self) -> Path | None: ...

    @override
    @property
    def path_provider(self) -> "FilePathProvider":
        return self._path_provider

    @override
    def get_path(self) -> Path:
        ret_path = self._get_file_path()
        return ret_path if ret_path else self.path_provider.get_path()


class EnvFilePathProvider(FilePathProvider):
    def __init__(self, env: str, path_provider: FilePathProvider):
        self.env = env
        super().__init__(path_provider)

    @override
    def _get_file_path(self) -> Path | None:
        env_val: str | None = os.getenv(self.env)
        return Path(env_val) if env_val is not None else None


class IniFilePathProvider(FilePathProvider):
    def __init__(
        self, path_provider: FilePathProvider, ini_file_path: Path = Path.cwd()
    ):
        super().__init__(path_provider)
        self.ini_file_path = Path(ini_file_path, "ittusa.ini")
        self.parser = configparser.ConfigParser()

    @override
    def _get_file_path(self) -> Path | None:
        if not self.ini_file_path.exists():
            return None
        self.parser.read_file(str(self.ini_file_path))
        file_path = self.parser.get("ittusa", "index_store")
        return Path(file_path) if file_path is not None else None


class PyprojectFilePathProvider(FilePathProvider):
    def __init__(
        self,
        path_provider: FilePathProvider,
        pyproject_root_file_path: Path = Path.cwd(),
    ):
        super().__init__(path_provider)
        self.pyproject_file_path = Path(pyproject_root_file_path, "pyproject.toml")

    @override
    def _get_file_path(self) -> Path | None:
        if not self.pyproject_file_path.exists():
            return None
        try:
            file_path = tomllib.loads(self.pyproject_file_path.read_text())["tool"][
                "ittusa"
            ]["ini"]["file_path"]
        except KeyError:
            return None
        return Path(file_path) if file_path is not None else None


class ConstTmpDirFPP(FilePathProvider):
    def __init__(
        self, file_path: Path = Path(tempfile.gettempdir(), ".0-LGCN-LOG-DETAILS.json")
    ):
        # Type ignoring arg of super().__init__() as FilePathProvider is required but None is provided
        super().__init__(None)  # type: ignore[arg-type]
        self.file_path = file_path

    @override
    def get_path(self) -> Path:
        return self._get_file_path()

    @override
    def _get_file_path(self) -> Path:
        return self.file_path


class FilePersister[DS](Persister, abc.ABC):
    def __init__(self, path_provider: PathProvider):
        self.file_path: Path = path_provider.get_path()

    def init(self):
        if not self.file_path.exists():
            self.file_path.write_text("")  # create the file


class JSONFilePersister(FilePersister[dict]):
    def commit(self, ds: dict):
        with open(self.file_path, mode="w+") as fp:
            json.dump(ds, fp)

    def reload(self) -> dict:
        try:
            return json.loads(self.file_path.read_text())
        except json.decoder.JSONDecodeError:
            return {}


class Repo(Protocol):
    """
    Repository that can:

    - initialise idempotently.
    - index (or store in memory) properties related to an object id.
    - commit the index to desired location. This is determined by the persister implementation.
    - reload (or refresh) the memory from the persister.
    - read the index (or memory) for retrieving properties relating to an object id.
    """

    @abstractmethod
    def init(self):
        """
        Initialise the repo.

        This will be an idempotent operation.

        It is required to be so because multiple classes/modules/packages may initialise the repo and it must not
        reinitialise its state every time.
        """
        ...

    @abstractmethod
    def index(self, id_: str, **attrs):
        """
        Store/Index the properties relating to ``id_`` in memory.

        :param id_: id to store properties for, in the memory.
        :param attrs: these properties will be stored against the ``id_``.
        """
        ...

    @abstractmethod
    def read(self, id_: str) -> dict[str, Any]:
        """
        Retrieve stored properties related to object ``_id`` from the index (or memory) without making expensive
        ``reload`` calls.

        Is an idempotent operation and does not contact the persister.

        :param id_: object id for which properties are to be queried from memory.
        :return: property-name -> property-value dictionary for the properties stored in-memory for object id ``id_``.
        """
        ...

    @abstractmethod
    def read_all(self) -> dict[str, dict[str, Any]]:
        """
        Retrieve all the stored properties related to all object ``_id`` from the index (or memory) without making
        expensive ``reload`` calls.

        Is an idempotent operation and does not contact the persister.

        :return: object-id -> {property-name -> property-value} dictionary for the properties stored in-memory for
            all object id(s).
        """
        ...

    @abstractmethod
    def reload(self):
        """
        Refresh the contents of memory or index by contacting the persister.
        """
        ...

    @abstractmethod
    def commit(self):
        """
        Persist in-memory to a persistent storage.

        Calls persister.
        """
        ...


class DictRepo(Repo):
    def __init__(self, persister: Persister[dict]):
        """
        Repo implementation using a ``defaultdict``.
        """
        self.repo: dict[str, dict[str, Any]] = defaultdict(dict)
        self.persister = persister

    @override
    def init(self):
        if self.repo is None:
            self.repo = defaultdict(dict)
        self.persister.init()

    @override
    def index(self, id_: str, **attrs):
        self.repo[id_].update(attrs)

    @override
    def read(self, id_: str) -> dict[str, Any]:
        return self.repo[id_].copy()

    def read_all(self) -> dict[str, dict[str, Any]]:
        return self.repo.copy()

    @override
    def commit(self):
        self.persister.commit(self.repo)

    @override
    def reload(self):
        self.repo = self.persister.reload()


__the_instance: Repo = DictRepo(
    JSONFilePersister(
        EnvFilePathProvider(
            LGCN_INFO_FP_ENV_VAR,
            EnvFilePathProvider(
                "ITTU_FP",
                IniFilePathProvider(PyprojectFilePathProvider(ConstTmpDirFPP())),
            ),
        )
    )
)


def get_repo() -> Repo:
    """
    :return: a singleton repo implementation.
    """
    return __the_instance
