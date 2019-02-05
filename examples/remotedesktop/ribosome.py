from uuid import uuid4
import _io
import io
import json

from autologging import traced

from brainslug.ribosome import define, root


powershell = root('powershell')

@define(powershell.bootloader)
def _(remote, **kwargs):
    return (
        r"""
        $CTX=@{}
        $URL=$args[0]
        $LAST=$null

        function Eval {
          Try {
            return (Invoke-Command -ScriptBlock (Invoke-Expression ("{{{0}}}" -f $args[0])))
          } Catch {
            return ConvertTo-Json @{type=$_.Exception.GetType().Name;
                                    message=$_.Exception.Message;
                                    stacktrace=$_.Exception.StackTrace}
          }
        }

        while ($true) {
          echo '------'
          $LAST=Eval(ConvertFrom-Json (Invoke-WebRequest -Uri $URL -Method Post -Body $LAST).content)
        }
        """)


@define(powershell.varname)
def _(remote, name):
    return f"$CTX.'{name}'"


@define(powershell.getitem)
def _(remote, name):
    return remote.eval(f"{remote.varname(name)} | ConvertTo-Json")


@define(powershell.setitem)
def _(remote, name, value):
    return remote.eval(f"{remote.varname(name)} = {value!r}")


@define(powershell.delitem)
def _(remote, name):
    return remote.eval(f"$CTX.Remove({name!r})")


@define(powershell.eval)
@traced
def _(remote, code, ignore_result=False, isbytes=False, isbytearray=False):
    raw = remote.__eval__(json.dumps(code))
    if ignore_result:
        return
    elif isbytes:
        return raw
    elif isbytearray:
        return bytes(map(int, raw.decode('ascii').split()))
    elif raw == b'':
        return None
    else:
        result = json.loads(raw.decode('utf-8'))
        if (isinstance(result, dict)
                and 'type' in result
                and 'message' in result
                and 'stacktrace' in result):
            raise RuntimeError(result['message'])
        else:
            return result


@define(powershell.File)
class _(io.RawIOBase):
    def __init__(self, remote, path):
        self.remote = remote
        self.path = path

    def close(self):
        pass

    def readable(self):
        return True

    def read(self, size=-1):
        raise NotImplementedError()

    def readall(self):
        return self.remote.eval(f"[io.file]::ReadAllBytes({self.path!r})", isbytearray=True)

    def readinto(self, b):
        raise NotImplementedError()

    def write(self, b):
        raise NotImplementedError()


@define(powershell.open)
def _(remote, file, mode='r', buffering=-1, encoding=None, errors=None,
      newline=None, closefd=True, opener=None):
    if 'b' in mode:
        if 'r' in mode:
            # return remote.File(file)
            return _io.BufferedReader(remote.File(file))
        elif 'w' in mode:
            return _io.BufferedWriter(remote.File(file))
    else:
        raise NotImplementedError()
        # return _io.TextIOWrapper(remote.File(file))


@define(powershell.mss.mss)
class _:
    def __init__(self, remote):
        self.remote = remote
        self.x = self.y = self.width = self.height = None

    def __enter__(self):
        self.remote.eval(f"""
            [Reflection.Assembly]::LoadWithPartialName("System.Drawing")
            function global:screenshot([Drawing.Rectangle]$bounds, $path) {{
               $bmp = New-Object Drawing.Bitmap $bounds.width, $bounds.height
               $graphics = [Drawing.Graphics]::FromImage($bmp)
               $graphics.CopyFromScreen($bounds.Location, [Drawing.Point]::Empty, $bounds.size)
               $bmp.Save($path)
               $graphics.Dispose()
               $bmp.Dispose()
            }}
        """,
        ignore_result=True)
        try:
            self.remote.eval(f"""
                [void][reflection.assembly]::Load('System.Windows.Forms, Version=2.0.0.0, Culture=neutral')
                $screens = [System.Windows.Forms.Screen]::AllScreens
            """)
        except RuntimeError:
            # Resolution not available, set the most common one
            self.x = self.y = 0
            self.width = 1366
            self.height = 768

        return self

    def __exit__(self, type, value, traceback):
        pass

    def shot(self):
        name = "monitor-1.png"
        remotepath = f"{name}"
        try:
            self.remote.eval(f"""
                $bounds = [Drawing.Rectangle]::FromLTRB({self.x}, {self.y}, {self.width}, {self.height})
                screenshot $bounds "{remotepath}"
                """)
        except RuntimeError as exc:
            raise IOError('Unable to take screenshot') from exc
        else:
            with self.remote.open(remotepath, 'rb') as remoteshot:
                with open(name, 'wb') as localshot:
                    localshot.write(remoteshot.read())
            return name
