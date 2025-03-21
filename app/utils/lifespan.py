from fastapi import FastAPI
from contextlib import asynccontextmanager
from time import perf_counter_ns

from ..database import events


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_time_ns: int = perf_counter_ns()
    app.state.start_time_ns = start_time_ns

    yield

    del app.state.start_time_ns
