from brainslug.ribosome import root, define


powershell = root('powershell')


@define(powershell.os.listdir)
def _(remote, path):
    print('cebolletas')
