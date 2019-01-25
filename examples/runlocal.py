import os

from brainslug import slug, run_locally, Brain


@slug(remote=Brain.platform == 'linux')
def test(remote):
    print(remote.os.listdir('/tmp'))

run_locally(test)
