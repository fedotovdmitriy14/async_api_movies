import asyncio
from typing import List

import aiohttp
import pytest
from elasticsearch import AsyncElasticsearch

from tests.functional.settings import test_settings
from tests.functional.utils.wait_for_es import wait_for_es
import pytest_asyncio


@pytest_asyncio.fixture(scope='session')
async def es_client():
    wait_for_es()
    client = AsyncElasticsearch(hosts=[f'http://{test_settings.elastic_host}:{test_settings.elastic_port}'])
    yield client
    await client.close()


@pytest.fixture(scope="session")
def event_loop():
    """Overrides pytest default function scoped event loop"""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope='session')
async def client_session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()
