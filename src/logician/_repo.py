#!/usr/bin/env python3
# coding=utf-8

"""
A repo implementation for observability of logger configurators.
"""
import json
import tempfile
from abc import abstractmethod
from collections import defaultdict
from pathlib import Path
from typing import Protocol, Any, override, Callable


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


class FilePersister[DS](Persister):
    def __init__(self, file_path_provider: Callable[[], Path] = lambda : Path(tempfile.gettempdir(), ".0-MY-LOG-DETAILS.json")):
        self.file_path: Path = file_path_provider()

    def init(self):
        if not self.file_path.exists():
            self.file_path.write_text("")   # create the file

    def commit(self, ds: DS):
        with open(self.file_path, mode="w+") as fp:
            json.dump(ds, fp)

    def reload(self) -> DS:
        return json.loads(self.file_path.read_text())


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
        return self.repo

    @override
    def commit(self):
        self.persister.commit(self.repo)

    @override
    def reload(self):
        self.repo = self.persister.reload()


__the_instance: Repo = DictRepo(FilePersister[dict]())


def get_repo() -> Repo:
    """
    :return: a singleton repo implementation.
    """
    return __the_instance
