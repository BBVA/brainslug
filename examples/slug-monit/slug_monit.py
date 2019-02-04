import json
import time
import threading
import http.server
import socketserver
import pickle

from brainslug import slug, run, body
from brainslug.ribosome import root, define


# ----------------------------------------- #
# Start Laguage Freak Zone
# ----------------------------------------- #
python = root('python')


@define(python._import)
def _(remote, name):
    return remote.remote_eval(f"exec('import {name}', globals())")


@define(python.pip.install)
def _(remote, *args):
    remote._import("subprocess")
    call_args = ["pip"] + args[0]
    command = f"subprocess.check_call({call_args})"
    remote.remote_eval(command)


@define(python.remote_eval)
def _(remote, code):
    raw = remote.__eval__(code)
    if not raw:
        return None
    res = pickle.loads(raw)
    if res and res[1]:
        raise res[1]
    else:
        return res[0]


@define(python.psutil.cpu_percent)
def _(remote, interval=0):
    return remote.remote_eval(f"psutil.cpu_percent(interval={interval})")


@define(python.psutil.virtual_memory)
def _(remote):
    return remote.remote_eval("psutil.virtual_memory()")


@define(python.psutil.disk_usage)
def _(remote, path):
    return remote.remote_eval(f"psutil.disk_usage('{path}')")


@define(python.psutil.net_io_counters)
def _(remote):
    return remote.remote_eval(f"psutil.net_io_counters()")


@define(python.psutil.boot_time)
def _(remote):
    return remote.remote_eval(f"psutil.boot_time()")


@define(python.socket.gethostname)
def _(remote):
    return remote.remote_eval(f"str(socket.gethostname())")


# ----------------------------------------- #
# End Laguage Freak Zone
# ----------------------------------------- #

def start_server():
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", 5500), handler) as httpd:
        print("server start on port 5500")
        httpd.serve_forever()


@slug(remote=body.__key__ == 'pepe')
def slug_monit(remote):
    t = threading.Thread(target=start_server)
    t.start()

    while True:
        try:
            remote._import("psutil")
            remote._import("socket")
        except Exception as exc:
            remote.pip.install(["install", "psutil"])
            remote._import("psutil")

        cpu = remote.psutil.cpu_percent(interval=1)
        mem = remote.psutil.virtual_memory()
        disk = remote.psutil.disk_usage("/")
        net = remote.psutil.net_io_counters()
        uptime = remote.psutil.boot_time()
        info = [{
                "name": remote.socket.gethostname(),
                "cpu": cpu,
                "mem": mem.used,
                "disk": disk.percent,
                "net_in": net.bytes_recv,
                "net_out": net.bytes_sent,
                "totals":{
                        "mem": mem.total,
                        "disk": disk.total,
                        "uptime": uptime
                    }
                }]
        print(info)
        with open("monit.json", "w") as fil:
            json.dump(info, fil)
        time.sleep(5)


run(slug_monit)
