import time
import threading

from brainslug import slug, run_locally, Brain
import psutil
from livereload import Server


def start_server():
    import asyncio
    asyncio.set_event_loop(asyncio.new_event_loop())
    s = Server()
    s.watch("*.json")
    s.serve()


@slug(remote=Brain.platform == 'linux')
def slug_monit(remote):
    t = threading.Thread(target=start_server)
    t.start()
    while True:
        info = {
                "cpu": remote.psutil.cpu_percent(interval=1),
                "mem": remote.psutil.virtual_memory().percent,
                "disk": remote.psutil.disk_usage("/").percent,
                "net_in": remote.psutil.net_io_counters().bytes_recv,
                "net_out": remote.psutil.net_io_counters().bytes_sent,
                "totals":{
                        "mem": remote.psutil.virtual_memory().total,
                        "disk": remote.psutil.disk_usage("/").total,
                        "uptime": remote.psutil.boot_time()
                    }
                }
        print(info)
        time.sleep(1)


run_locally(slug_monit)
