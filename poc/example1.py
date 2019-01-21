from brainslug import Runner

@app(master=(Remote.type == 'linux' & Limit(1)),
     slaves=(Remote.type == 'linux'))
def backup(master, slaves):
    for slave in slaves:
        for filename in slave.os.listdir('/etc'):
            with master.open('/something.tar') as dst:
                with slave.open(filename) as src:
                    m = src.read()
                    with Runner.select((Remote.machine_id == m)) as monitor:
                        monitor.os.list
