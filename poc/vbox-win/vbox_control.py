import virtualbox
from retrying import retry

def main():
    @retry(stop_max_attempt_number=100, wait_fixed=6000)
    def try_to_execute(con, s):
        try:
            print("try to execute command")
            proc, out, err = con.execute(
                'C:\\Windows\\System32\\cmd.exe',
                ['/C', 'tasklist']
            )
            print(out)
            print(err)
            s.console.power_down()
        except virtualbox.library_base.VBoxError as e:
            print("but not ready", e)
            raise e
    print("start machine")
    vbox = virtualbox.VirtualBox()

    vm = vbox.find_machine('MSEdge - Win10')
    vm.launch_vm_process()
    ss = vm.create_session()
    console = ss.console.guest.create_session('IEUSER', 'Passw0rd!')
    try_to_execute(console, ss)

main()