"""Execute the production Lua callbacks against isolated snapshots and UI geometry."""

import ctypes
import ctypes.util
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

from cortex_neo.io import lua

ROOT = Path(__file__).resolve().parents[1]


class LuaHarness:
    def __init__(self, snapshot, scale=1, ui=None):
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name)
        (self.root / "dashboard.lua").write_text("return " + lua(snapshot), encoding="utf-8")
        self.ui = dict(
            scale=scale,
            font_scale=scale,
            padding=round(14 * scale),
            cards=dict(
                software=dict(width=344 * scale, height=792 * scale),
                storage=dict(width=320 * scale, height=248 * scale),
            ),
        )
        self.ui.update(ui or {})
        (self.root / "ui.lua").write_text("return " + lua(self.ui), encoding="utf-8")
        self.environment = patch.dict(
            os.environ,
            {
                "CORTEX_NEO_THEME_DIR": str(ROOT / "theme"),
                "CORTEX_NEO_CACHE_DIR": str(self.root),
                "CORTEX_NEO_UI_FILE": str(self.root / "ui.lua"),
                "CORTEX_NEO_PRESENTATION_FILE": "",
            },
        )
        self.environment.start()
        library = ctypes.util.find_library("lua5.4") or ctypes.util.find_library("lua5.3")
        if not library:
            raise RuntimeError("Lua shared library is required for renderer tests")
        self.lua = ctypes.CDLL(library)
        self.lua.luaL_newstate.restype = ctypes.c_void_p
        for function, args in {
            "luaL_openlibs": [ctypes.c_void_p],
            "luaL_loadfilex": [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p],
            "lua_pcallk": [
                ctypes.c_void_p,
                ctypes.c_int,
                ctypes.c_int,
                ctypes.c_int,
                ctypes.c_longlong,
                ctypes.c_void_p,
            ],
            "lua_getglobal": [ctypes.c_void_p, ctypes.c_char_p],
            "lua_pushstring": [ctypes.c_void_p, ctypes.c_char_p],
            "lua_tolstring": [ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p],
            "lua_settop": [ctypes.c_void_p, ctypes.c_int],
            "lua_close": [ctypes.c_void_p],
        }.items():
            getattr(self.lua, function).argtypes = args
        self.lua.lua_tolstring.restype = ctypes.c_char_p
        self.state = self.lua.luaL_newstate()
        self.lua.luaL_openlibs(self.state)
        code = self.lua.luaL_loadfilex(self.state, str(ROOT / "theme/formatter.lua").encode(), None)
        self.check(code)
        self.check(self.lua.lua_pcallk(self.state, 0, 0, 0, 0, None))

    def check(self, code):
        if code:
            raise AssertionError(self.lua.lua_tolstring(self.state, -1, None).decode())

    def call(self, name, *args):
        self.lua.lua_getglobal(self.state, ("conky_" + name).encode())
        for arg in args:
            self.lua.lua_pushstring(self.state, str(arg).encode())
        self.check(self.lua.lua_pcallk(self.state, len(args), 1, 0, 0, None))
        value = self.lua.lua_tolstring(self.state, -1, None)
        result = value.decode() if value else ""
        self.lua.lua_settop(self.state, 0)
        return result

    def close(self):
        self.lua.lua_close(self.state)
        self.environment.stop()
        self.directory.cleanup()
