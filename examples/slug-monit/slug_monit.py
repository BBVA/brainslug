import time

from brainslug import slug, run_locally, Brain
import psutil

@slug(remote=Brain.platform == 'linux')
def slug_monit(remote):
    while True:
        info = {
                "cpu": psutil.cpu_percent(interval=1),
                "mem": psutil.virtual_memory().percent,
                "disk": psutil.disk_usage("/").percent,
                "net_in": psutil.net_io_counters().bytes_recv,
                "net_out": psutil.net_io_counters().bytes_sent,
                "totals":{
                        "mem": psutil.virtual_memory().total,
                        "disk": psutil.disk_usage("/").total,
                        "uptime": psutil.boot_time()
                    }
                }
        print(info)
        time.sleep(1)
        

run_locally(slug_monit)
