import pytest
import asyncio

from brainslug.webapp import process_agent_request


def test_process_agent_request_is_a_function():
    assert callable(process_agent_request), "process_agent_request must be a function"


