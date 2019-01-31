import json
import time
import threading
import http.server
import socketserver

from brainslug import slug, run, Brain
import psutil


def start_server():
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", 5500), handler) as httpd:
        print("server start on port 5500")
        httpd.serve_forever()


@slug(remote=Brain.platform == 'linux')
def slug_monit(remote):
    t = threading.Thread(target=start_server)
    t.start()
    while True:
        info = [{
                "name": "remote",
                "cpu": remote.psutil.cpu_percent(interval=1),
                "mem": remote.psutil.virtual_memory().used,
                "disk": remote.psutil.disk_usage("/").percent,
                "net_in": remote.psutil.net_io_counters().bytes_recv,
                "net_out": remote.psutil.net_io_counters().bytes_sent,
                "totals":{
                        "mem": remote.psutil.virtual_memory().total,
                        "disk": remote.psutil.disk_usage("/").total,
                        "uptime": remote.psutil.boot_time()
                    }
                },{
                "name": "other",
                "cpu": remote.psutil.cpu_percent(interval=1),
                "mem": remote.psutil.virtual_memory().used,
                "disk": remote.psutil.disk_usage("/").percent,
                "net_in": remote.psutil.net_io_counters().bytes_recv,
                "net_out": remote.psutil.net_io_counters().bytes_sent,
                "totals":{
                        "mem": remote.psutil.virtual_memory().total,
                        "disk": remote.psutil.disk_usage("/").total,
                        "uptime": remote.psutil.boot_time()
                    }
                }]
        with open("monit.json", "w") as fil:
            json.dump(info, fil)
        time.sleep(5)


run(slug_monit, local=True)
