"""One sqlite3 connection, safely shared between threads.

MEASURED, and the second half is the part that is not obvious. Lifting
sqlite3's own thread check (check_same_thread=False) is necessary and not
sufficient: with eight threads writing through one connection, sqlite3
raised OperationalError('not an error') -- a real race with a misleading
message -- even though this build reports threadsafety 3 (SERIALIZED).

So every statement is serialised here, with the lock held across execute
AND the fetch, because a cursor read lazily on another thread is the same
race as the write. Rows come back already materialised.

Both stores that outlive a request use this: the memory store, and the
vault index's FTS5 connection. The vault one was found by running the
application -- unit tests all ran on a single thread and never saw it.
"""
from __future__ import annotations

import threading


class Rows(list):
    """Materialised rows that still answer like a cursor."""
    def __init__(self, rows, lastrowid=None, rowcount=-1):
        super().__init__(rows)
        self.lastrowid = lastrowid
        self.rowcount = rowcount

    def fetchall(self):
        return list(self)

    def fetchone(self):
        return self[0] if self else None


class LockedConnection:
    """A sqlite3 connection that may be shared between threads.

    The lock is held across execute *and* the fetch, because a cursor read
    lazily on another thread is the same race as the write.
    """

    def __init__(self, conn):
        self._conn = conn
        self._lock = threading.RLock()
        self.row_factory = None

    def __setattr__(self, name, value):
        if name in ("_conn", "_lock", "row_factory"):
            object.__setattr__(self, name, value)
            if name == "row_factory" and getattr(self, "_conn", None) is not None:
                self._conn.row_factory = value
        else:
            setattr(self._conn, name, value)

    def execute(self, sql, params=()):
        with self._lock:
            cur = self._conn.execute(sql, params)
            rows = cur.fetchall() if cur.description else []
            return Rows(rows, cur.lastrowid, cur.rowcount)

    def executemany(self, sql, seq):
        with self._lock:
            cur = self._conn.executemany(sql, seq)
            return Rows([], cur.lastrowid, cur.rowcount)

    def executescript(self, sql):
        with self._lock:
            return self._conn.executescript(sql)

    def commit(self):
        with self._lock:
            return self._conn.commit()

    def close(self):
        with self._lock:
            return self._conn.close()

    def __getattr__(self, name):
        return getattr(self._conn, name)
