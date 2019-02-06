from uuid import uuid4
import _io
import io
import json
import base64
import requests

from autologging import traced

from brainslug.ribosome import define, root


powershell = root('powershell')


@define(powershell.boot)
def _(remote, url, **kwargs):
    return (
        f"""
        $CTX=@{{}}
        $URL="{url}"
        $LAST=$null

        function Eval {{
          Try {{
            return (Invoke-Command -ScriptBlock (Invoke-Expression ("{{{{{{0}}}}}}" -f $args[0])))
          }} Catch {{
            return ConvertTo-Json @{{type=$_.Exception.GetType().Name;
                                    message=$_.Exception.Message;
                                    stacktrace=$_.Exception.StackTrace}}
          }}
        }}

        while ($true) {{
          echo '------'
          $LAST=Eval(ConvertFrom-Json (Invoke-WebRequest -Uri $URL -Method Post -Body $LAST -UseBasicParsing).content)
        }}
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
                [void] [System.Reflection.Assembly]::LoadWithPartialName("System.Windows.Forms")
            """, ignore_result=True)
        except RuntimeError:
            # Resolution not available, set the most common one
            self.x = self.y = 0
            self.width = 1366
            self.height = 768
            print(f'Using FAILOVER screen resolution {self.width}x{self.height}.')
        else:
            screens = self.remote.eval(f'[System.Windows.Forms.Screen]::AllScreens | ConvertTo-Json')
            if isinstance(screens, dict):
                screens = [screens]
            primary = screens[0]
            self.x = primary['Bounds']['X']
            self.y = primary['Bounds']['Y']
            self.width = primary['Bounds']['Width']
            self.height = primary['Bounds']['Height']
            print(f'Using screen resolution {self.width}x{self.height}.')

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

@define(powershell.pyautogui.press)
def _(remote, key):
    if len(key) > 1:
        key = f'{{{key.upper()}}}'

    remote.eval(f"""
        [void] [System.Reflection.Assembly]::LoadWithPartialName("System.Windows.Forms")
        [System.Windows.Forms.SendKeys]::SendWait("{key}")
    """, ignore_result=True)



@define(powershell.pyautogui.moveTo)
def _(remote, x, y):
    remote.eval(f"""
        [void] [System.Reflection.Assembly]::LoadWithPartialName("System.Windows.Forms")
        $position = [System.Windows.Forms.Cursor]::Position
        $position.X = {x}
        $position.Y = {y}
        [System.Windows.Forms.Cursor]::Position = $position
    """, ignore_result=True)


@define(powershell.pyautogui.click)
def _(remote, x, y, button='left'):
    remote.pyautogui.moveTo(x, y)
    remote.eval(r"""
        [CmdletBinding()]
        param($Interval = 5000, [switch]$RightClick, [switch]$NoMove)

        [Reflection.Assembly]::LoadWithPartialName("System.Drawing")
        $DebugViewWindow_TypeDef = @'
        [DllImport("user32.dll")]
        public static extern IntPtr FindWindow(string ClassName, string Title);
        [DllImport("user32.dll")]
        public static extern IntPtr GetForegroundWindow();
        [DllImport("user32.dll")]
        public static extern bool SetCursorPos(int X, int Y);
        [DllImport("user32.dll")]
        public static extern bool GetCursorPos(out System.Drawing.Point pt);

        [DllImport("user32.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.StdCall)]
        public static extern void mouse_event(long dwFlags, long dx, long dy, long cButtons, long dwExtraInfo);

        private const int MOUSEEVENTF_LEFTDOWN = 0x02;
        private const int MOUSEEVENTF_LEFTUP = 0x04;
        private const int MOUSEEVENTF_RIGHTDOWN = 0x08;
        private const int MOUSEEVENTF_RIGHTUP = 0x10;

        public static void LeftClick(){
            mouse_event(MOUSEEVENTF_LEFTDOWN | MOUSEEVENTF_LEFTUP, 0, 0, 0, 0);
        }

        public static void RightClick(){
            mouse_event(MOUSEEVENTF_RIGHTDOWN | MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0);
        }
'@
        Add-Type -MemberDefinition $DebugViewWindow_TypeDef -Namespace AutoClicker -Name Temp -ReferencedAssemblies System.Drawing
        """ +
        ("[AutoClicker.Temp]::RightClick()"
         if button == 'right'
         else "[AutoClicker.Temp]::LeftClick()"), ignore_result=True)


browser = root('browser')


@define(browser.boot)
def _(remote, url, **kwargs):
    return (f"""
        function dowhat(res) {{
            var httpfirst = new XMLHttpRequest();
            httpfirst.open('POST', '{url}', true);
            httpfirst.onreadystatechange = (evt) => {{
                if (httpfirst.readyState == 4 && httpfirst.status == 200) {{
                    eval(httpfirst.response)(dowhat);
                }}
            }};
            httpfirst.send(res);
        }}
        dowhat(() => null);
        """)


@define(browser.eval)
@traced
def _(remote, code, ignore_result=False):
    result = remote.__eval__(code.encode('utf-8'))
    if not ignore_result:
        try:
            return json.loads(result)
        except:
            return result

@define(browser.require)
def _(remote, url):
    code = requests.get(url).text
    remote.eval(f"""
        (res) => {{
            {code}
        res();
        }}""",
        ignore_result=True)


@define(browser.mss.mss)
class _:
    def __init__(self, remote):
        self.remote = remote

    def __enter__(self):
        self.remote.require('https://html2canvas.hertzen.com/dist/html2canvas.min.js')
        return self

    def __exit__(self, type, value, traceback):
        pass

    def shot(self):
        res = self.remote.eval("""
            (res) => {
                html2canvas(document.body, {type: 'view'}).then(function (canvas) {
                    res(JSON.stringify(canvas.toDataURL('image/png')));
                });
            }
        """)
        path = 'monitor-1.png'
        with open(path, 'wb') as localfile:
            localfile.write(base64.b64decode(res.split(',')[1]))
        return path


@define(browser.pyautogui.press)
def _(remote, key):
    self.remote.eval("""
        (res) => {
            document.elementFromPoint(x, y).
            res();
        }""",
        ignore_result=True)


@define(browser.pyautogui.moveTo)
def _(remote, x, y):
    pass


@define(browser.pyautogui.click)
def _(remote, x, y, button='left'):
    self.remote.eval("""
        (res) => {
            document.elementFromPoint(x, y).click();
            res();
        }""",
        ignore_result=True)
