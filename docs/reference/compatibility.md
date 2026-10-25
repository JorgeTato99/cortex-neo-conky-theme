# Compatibility

Python **3.11+** is required. Logic/Lua CI covers 3.11, 3.12, 3.13, 3.14 and 3.15. Each installation uses one distribution interpreter inside a venv with OS GTK bindings. A newer Python test does not establish GTK compatibility for an independently installed interpreter on every distribution. Python 3.10 is rejected before package/file mutations; standard Ubuntu 22.04's default interpreter is outside automatic profiles.

| Environment | Evidence scope |
|---|---|
| Ubuntu 26.04.1 / GNOME Wayland / Intel and NVIDIA x86_64 | Two physical machines; native install, units, metrics and window bounds |
| Ubuntu 24.04/26.04, Debian 12/13 | Clean container installation/reinstallation/removal plus real Conky/Xvfb render |
| Python 3.11–3.15 | Logic, files and real Lua callbacks; not five physical desktops |
| Linux ARM64 | Native CI logic/Lua; not sensor or compositor certification for a board |
| AMD | DRM fixtures; no claim of physical AMD GPU validation |
| Other distributions/desktops | Experimental manual dependencies; graphical behavior unverified |

These are independent evidence layers, not the Cartesian product of every OS, Python, GPU and desktop combination. Conky needs X11 and Lua; Wayland needs XWayland. Generator settings adapt to older/newer Conky builds. Missing Docker, sensors, compilers or city remain optional rather than causing fictional readings.

Three font profiles are supported; unavailable families are substituted explicitly through fontconfig. Ten palette categories match the observed Ubuntu 26 accent enum. Appearance does not require changing the system accent or desktop font.

Primary references: [Python lifecycle](https://devguide.python.org/versions/), [PyGObject](https://pygobject.gnome.org/getting_started.html), [Conky](https://conky.cc/config_settings), [GitHub runners](https://docs.github.com/en/actions/how-tos/write-workflows/choose-where-workflows-run/choose-the-runner-for-a-job).
