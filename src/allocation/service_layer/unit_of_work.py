# pylint: disable=attribute-defined-outside-init
from __future__ import annotations
import abc
from typing import ContextManager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

from allocation import config
from allocation.adapters import repository
from contextlib import contextmanager


class AbstractUnitOfWork(abc.ABC):
    # should this class contain __enter__ and __exit__?
    # or should the context manager and the UoW be separate?
    # up to you!
    @abc.abstractmethod
    def commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self):
        raise NotImplementedError

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_value is not None:
            self.rollback()

DEFAULT_SESSION_FACTORY = sessionmaker(
    bind=create_engine(
        config.get_postgres_uri(),
    )
)

class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self):
        self.session = DEFAULT_SESSION_FACTORY()
        self.repository = repository.SqlAlchemyRepository(self.session)

    def __enter__(self):
        return self

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()





# One alternative would be to define a `start_uow` function,
# or a UnitOfWorkStarter or UnitOfWorkManager that does the
# job of context manager, leaving the UoW as a separate class
# that's returned by the context manager's __enter__.
#
# A type like this could work?
# AbstractUnitOfWorkStarter = ContextManager[AbstractUnitOfWork]
