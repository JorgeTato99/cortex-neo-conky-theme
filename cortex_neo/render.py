"""Generate Conky configs from maintained text templates and one scale factor."""

import json
import math
import re
import tempfile
from pathlib import Path

from .conky import window_settings
from .fonts import resolve_font
from .i18n import catalog
from .io import atomic, lua
from .paths import CACHE, GENERATED, ROOT
from .preferences import theme_settings

TITLES = {
    "system": ("\uf108", "CORTEX NEO"),
    "cpu": ("\uf2db", "PROCESSOR"),
    "ram": ("\uf1b2", "MEMORY"),
    "gpu": ("\uf108", "GRAPHICS"),
    "storage": ("\uf0a0", "STORAGE"),
    "network": ("\uf0ac", "NETWORK / CONTAINERS"),
    "software": ("\uf121", "VERSIONS / BUILDS"),
    "calendar": ("\uf073", "CALENDAR"),
    "weather": ("\uf041", "LOCATION / WEATHER"),
}


def scaled_text(text, scale, font_adjustment=1, minimum_font=1):
    def number(value):
        return str(max(minimum_font, math.floor(int(value) * scale * font_adjustment + 0.5)))

    text = re.sub(r"(\$\{font[^}]*?size=)(\d+)", lambda m: m[1] + number(m[2]), text)
    for key in ("voffset", "offset"):
        text = re.sub(
            r"(\$\{" + key + r"\s+)(-?\d+)",
            lambda m: m[1] + str(math.floor(int(m[2]) * scale + 0.5)),
            text,
        )
    text = re.sub(
        r"(lua_graph\s+\w+\s+)(\d+),",
        lambda m: m[1] + str(max(1, round(int(m[2]) * scale))) + ",",
        text,
    )
    return text


def config(name, box, layout, snapshot, build=None):
    scale = layout["scale"]
    theme = theme_settings(layout.get("theme"))
    colors = theme["colors"]
    family = resolve_font(layout.get("font", "ubuntu"))
    padding = max(1, round(14 * scale))
    content_width = max(1, round(box["w"]) - 2 * padding)
    graph_width = max(1, content_width - round(4 * scale))
    text = (ROOT / "theme/cards" / (name + ".conky")).read_text(encoding="utf-8").strip()
    gpu = snapshot.get("gpu", {}) or {}
    graphics = []
    if gpu.get("load") is not None:
        graphics.append(
            "${if_match ${lua has gpu.load} == 1}${color1}${lua_graph gpu_load 30,@GRAPH_WIDTH@ 183451 55AEFF 100}${endif}"
        )
    elif gpu.get("frequency") is not None:
        ceiling = gpu.get("frequency_max") or 0
        graphics.append(
            "${if_match ${lua has gpu.frequency} == 1}${color1}${lua_graph gpu_frequency 54,@GRAPH_WIDTH@ 183451 55AEFF "
            + str(ceiling)
            + "}${endif}"
        )
    if gpu.get("memory_load") is not None:
        graphics.extend(
            [
                "${color2}${font Ubuntu Sans Mono:size=8}${lua vram_usage}${font}",
                "${if_match ${lua has gpu.memory_load} == 1}${color2}${lua_graph vram_load 24,@GRAPH_WIDTH@ 183451 6DE4EF 100}${endif}",
            ]
        )
    text = text.replace("@GPU_GRAPHS@", "\n".join(graphics))
    network = ""
    if (snapshot.get("network") or {}).get("interface"):
        network = (
            "${color3}${lua network_label}\n"
            "${color2}DOWN ${lua net_rx_text}${goto @NETWORK_SECOND@}${color1}UP ${lua net_tx_text}\n"
            "${if_match ${lua has network.rx} == 1}${color2}${lua_graph net_rx 48,@NETWORK_WIDTH@ 183451 6DE4EF 0}${offset 16}${color1}${lua_graph net_tx 48,@NETWORK_WIDTH@ 183451 55AEFF 0}${endif}"
        )
    text = text.replace("@NETWORK_METRICS@", network)
    docker = (
        "${voffset 4}${color2}DOCKER${alignr}${color}${font Ubuntu Sans Mono:size=9}${lua containers}${font}"
        if snapshot.get("docker_available")
        else ""
    )
    text = text.replace("@DOCKER_STATUS@", docker)
    text = re.sub(r",288(?=\s)", ",@GRAPH_WIDTH@", text)
    text = text.replace("@GRAPH_WIDTH@", str(graph_width))
    text = text.replace("@CONTENT_WIDTH@", str(content_width))
    half = max(1, round((content_width - round(20 * scale)) / 2))
    text = text.replace("@NETWORK_WIDTH@", str(half))
    text = text.replace("@NETWORK_SECOND@", str(padding + half + round(16 * scale)))
    text = text.replace("@PADDING@", str(padding))
    if "@" in text:
        raise ValueError(f"Unexpanded theme token in {name}")
    glyph, title = TITLES[name]
    if name == "network":
        if not snapshot.get("docker_available"):
            title = "NETWORK"
        elif not (snapshot.get("network") or {}).get("interface"):
            title = "CONTAINERS"
    title = catalog(layout.get("language", "en")).get(title, title)
    if name == "cpu":
        text = text.replace("history / 2s", "historial / 2s" if layout.get("language") == "es" else "history / 2s")
    status = "${lua_parse status}" if name == "system" else "${color4}┐"
    header = (
        "${font FontAwesome:size=13}${color2}"
        + glyph
        + "${font Ubuntu Sans Mono:style=Bold:size=10}${color1}  "
        + title
        + "${font}${alignr}"
        + status
        + "\n${color4}${hr 1}${color}\n"
    )
    text = header + text
    for source, target in (("55AEFF", colors["primary"]), ("6DE4EF", colors["secondary"]), ("183451", colors["graph"])):
        text = text.replace(source, target)
    text = text.replace("Ubuntu Sans Mono", family)
    text = scaled_text(
        text, scale, layout.get("font_adjustment", 1), layout.get("min_font_size", 7)
    )
    backend, color = window_settings(build, theme)
    return f"""-- Generated by CORTEX NEO. Edit theme/cards/ and cortex_neo/render.py.
conky.config={{
{backend}background=false,update_interval=2,
double_buffer=true,no_buffers=true,cpu_avg_samples=2,
own_window=true,own_window_type='normal',own_window_class='Conky',own_window_title='Cortex Neo - {name}',
own_window_hints='undecorated,below,sticky,skip_taskbar,skip_pager',
{color}
alignment='top_left',gap_x={round(layout["x"] + box["x"]) + padding},gap_y={round(layout["y"] + box["y"]) + padding},
minimum_width={content_width},maximum_width={content_width},minimum_height={max(1, round(box["h"]) - 2 * padding)},
border_inner_margin={padding},border_outer_margin=0,border_width=0,
use_xft=true,font='{family}:size={max(layout.get("min_font_size", 7), round(10 * scale * layout.get("font_adjustment", 1)))}',xftalpha=1,override_utf8_locale=true,
draw_shades=false,draw_outline=false,draw_borders=false,draw_graph_borders=true,
default_color='{colors["text"]}',color1='{colors["primary"]}',color2='{colors["secondary"]}',color3='{colors["muted"]}',
color4='{colors["border"]}',color5='{colors["accent"]}',color6='{colors["warning"]}',text_buffer_size=32768,max_user_text=65536,
lua_load={lua(str(ROOT / "theme/formatter.lua"))},
}}
conky.text=[=[{text}]=]
"""


def generate(layout, snapshot, build=None):
    """Stage a complete generation before the supervisor replaces live windows."""
    GENERATED.mkdir(parents=True, exist_ok=True, mode=0o700)
    directory = Path(tempfile.mkdtemp(prefix="generation-", dir=GENERATED))
    ui = dict(
        scale=layout["scale"],
        font_scale=layout["scale"] * layout.get("font_adjustment", 1),
        min_font_size=layout.get("min_font_size", 7),
        density=layout.get("density", "complete"),
        presentation_profile=layout.get("presentation_profile", "full"),
        top_count=layout.get("top_count", 5),
        font_family=resolve_font(layout.get("font", "ubuntu")),
        language=layout.get("language", "en"),
        detail_level=layout.get("detail_level", "full"),
        translations=catalog(layout.get("language", "en")),
        weekdays=["L", "M", "X", "J", "V", "S", "D"] if layout.get("language") == "es" else ["M", "T", "W", "T", "F", "S", "S"],
        padding=max(1, round(14 * layout["scale"])),
        cards={k: dict(width=v["w"], height=v["h"]) for k, v in layout["cards"].items()},
    )
    for name, box in layout["cards"].items():
        atomic(directory / (name + ".conf"), config(name, box, layout, snapshot, build))
    atomic(directory / "ui.lua", "return " + lua(ui) + "\n")
    atomic(CACHE / "layout.json", json.dumps(layout, indent=2))
    return directory
