from unittest.mock import MagicMock as Mock
from unittest.mock import patch
import threading

import pytest

from brainslug.utils import to_remote


@pytest.mark.asyncio
async def test_to_remote_builds_a_safe_lambda(event_loop):
    code = object()
    result = object()
    future = Mock()
    future.result.return_value = result

    with patch('asyncio.run_coroutine_threadsafe', return_value=future) as rct:
        channel = Mock()
        doc = {'__language__': lambda x: [x], '__channel__': channel}

        # Language is instantiated with the lambda 
        [_run_threadsafe] = to_remote(event_loop, doc)

        assert _run_threadsafe(code) is result  # We call the generated lambda
        channel.remote_eval.assert_called_once_with(code)
        rct.assert_called_once_with(channel.remote_eval(code), event_loop)
