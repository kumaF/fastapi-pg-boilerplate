from sqlalchemy import event
from time import perf_counter_ns

from .core import async_engine

from ..utils.cache import set_cache
from ..utils.request import get_request_id


@event.listens_for(async_engine.sync_engine, 'before_cursor_execute')
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    context._query_start_time = perf_counter_ns()


@event.listens_for(async_engine.sync_engine, 'after_cursor_execute')
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    end_time = perf_counter_ns()
    duration_ns = end_time - context._query_start_time
    set_cache(get_request_id(), duration_ns)
