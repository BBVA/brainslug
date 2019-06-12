Running this demo
=================

To run this demo you'll need:

* Python 3.7
* Pipenv

Access this directory and type:

```bash
$ pipenv sync
$ pipenv run python remotedesktop.py
```

With the `Slug` running you can get the code needed to spawn the PowerShell
`Zombie` visiting the URL:

```plain
http://localhost:8080/launch/powershell
```

or to launch the body in a browser:

```plain
http://localhost:8080/launch/browser
```

After the `Zombie` connects to the `Slug` a webserver will be launched at
http://localhost:8091 which you can use to see the `Zombie` screen.
