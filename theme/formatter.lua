-- Conky callbacks. Live data, pixel scaling and escaping are shared by helpers.
local H = dofile(os.getenv("CORTEX_NEO_THEME_DIR") .. "/helpers.lua")
local data = H.data
local function bytes(n)
    if type(n) ~= "number" then
        return "—"
    end
    return string.format("%.1f GiB", n / 1024 ^ 3)
end
function conky_value(path)
    local value = data()
    for key in path:gmatch("[^.]+") do
        value = type(value) == "table" and value[tonumber(key) or key] or nil
    end
    return (type(value) == "string" or type(value) == "number") and tostring(value) or ""
end
local function flow(n)
    if type(n) ~= "number" or not H.fresh() then
        return "—"
    end
    return n > 1024 ^ 2 and string.format("%.1f MiB/s", n / 1024 ^ 2)
        or string.format("%.1f KiB/s", n / 1024)
end
function conky_network_label()
    local n = data().network or {}
    if H.private_mode() then
        return n.kind or "Red"
    end
    return (n.kind or "") .. " / " .. (n.interface or "")
end
function conky_net_rx_text()
    return flow((data().network or {}).rx)
end
function conky_net_tx_text()
    return flow((data().network or {}).tx)
end
function conky_gpu_load()
    return (data().gpu or {}).load or 0
end
function conky_cpu_load()
    return (data().cpu or {}).load or 0
end
function conky_ram_load()
    return (data().ram or {}).load or 0
end
function conky_cpu_usage()
    local n = (data().cpu or {}).load
    return H.fresh() and type(n) == "number" and string.format("%.1f%%", n) or "—"
end
function conky_ram_usage()
    local n = (data().ram or {}).load
    return H.fresh() and type(n) == "number" and string.format("%.1f%%", n) or "—"
end
function conky_vram_load()
    return (data().gpu or {}).memory_load or 0
end
function conky_disk_load()
    return ((data().disks or {})[1] or {}).load or 0
end
function conky_cpu_temp()
    local t = (data().cpu or {}).temperature
    return H.fresh() and type(t) == "number" and string.format("%.0f C", t) or ""
end
function conky_gpu_frequency()
    return (data().gpu or {}).frequency or 0
end
function conky_net_rx()
    return ((data().network or {}).rx or 0) / 1024
end
function conky_net_tx()
    return ((data().network or {}).tx or 0) / 1024
end
function conky_vram_usage()
    local g = data().gpu or {}
    if not H.fresh() or type(g.memory_load) ~= "number" then
        return "—"
    end
    return string.format("VRAM %.1f%% / ", g.memory_load or 0)
        .. bytes(g.used)
        .. " / "
        .. bytes(g.total)
end
function conky_disk_usage()
    local d = (data().disks or {})[1] or {}
    if not H.fresh() or type(d.load) ~= "number" then
        return "—"
    end
    return (H.private_mode() and "[montaje]" or H.clean(d.target or "/"))
        .. string.format(" · USO %.1f%% / ", d.load or 0)
        .. bytes(d.used)
        .. " / "
        .. bytes(d.total)
end
function conky_memory_usage()
    if not H.fresh() then
        return "—"
    end
    local r = data().ram or {}
    local usage = bytes(r.used) .. " / " .. bytes(r.total)
    if type(r.available) == "number" then
        usage = usage .. " · disp " .. string.format("%.1fG", r.available / 1024 ^ 3)
    end
    return usage
end
function conky_containers()
    local out = {}
    local projects = 0
    local configured = {}
    for _, key in ipairs(data().docker_contexts or {}) do
        configured[key] = true
    end
    for _, p in ipairs({ { "default", "Engine" }, { "desktop-linux", "Desktop" } }) do
        local v = (data().docker or {})[p[1]]
        if configured[p[1]] or v then
            local available = v and v.status ~= "unavailable" and type(v.running) == "number"
            if available and type(v.sampled_at) == "number" and os.time() - v.sampled_at > 45 then
                available = false
            end
            if available then
                projects = projects + (v.project_count or 0)
            end
            out[#out + 1] = p[2]
                .. ": "
                .. (
                    available
                        and tostring(v.running) .. (H.ui.presentation_profile == "compact" and "" or " activos")
                    or "sin conexión"
                )
        end
    end
    return table.concat(out, " / ") .. (projects > 0 and (" · " .. projects .. " grupos") or "")
end
local function clean(text)
    return tostring(text or ""):gsub("[$%c]", " ")
end
local function number(value, format)
    return type(value) == "number" and string.format(format or "%.0f", value) or "--"
end
local function condition(code, is_day)
    if code == 0 or code == 1 then
        return code == 0 and "Despejado" or "Mayormente despejado",
            is_day == 0 and "\u{f186}" or "\u{f185}"
    end
    if code == 2 or code == 3 then
        return code == 2 and "Parcialmente nublado" or "Nublado", "\u{f0c2}"
    end
    if code == 45 or code == 48 then
        return "Niebla", "\u{f0c2}"
    end
    if code and code >= 95 then
        return "Tormenta", "\u{f0e7}"
    end
    if code and ((code >= 71 and code <= 77) or code == 85 or code == 86) then
        return "Nieve", "\u{f2dc}"
    end
    if code and code >= 51 and code <= 57 then
        return "Llovizna", "\u{f043}"
    end
    if code and code >= 61 and code <= 82 then
        return "Lluvia", "\u{f043}"
    end
    return "Sin dato", "\u{f0c2}"
end
function conky_weather()
    if H.private_mode() then
        return "${color3}Ubicación y clima ocultos"
    end
    local w = data().weather or { status = "unconfigured" }
    if w.status == "unconfigured" then
        return "${color}${font Ubuntu Sans Mono:style=Bold:size=12}TU UBICACION${font}\n\n${color3}Pendiente de configurar ciudad.\n\nClima actual y pronostico\nde los proximos siete dias.\n\n${color2}${font FontAwesome:size=24}\u{f0c2}${font}\n\n${color3}${font Ubuntu Sans Mono:size=8}Sin geolocalizacion por IP.\nFuente: Open-Meteo${font}"
    end
    local place = w.location or {}
    local weather_card = (H.ui.cards or {}).weather or { width = 272 }
    local width = weather_card.width - 2 * (H.ui.padding or 14)
    local lines = {
        "${font Ubuntu Sans Mono:style=Bold:size=12}${color}"
            .. H.short(place.name, math.floor(width / (H.font(12) * 0.8))),
        "${font Ubuntu Sans Mono:size=9}${color3}"
            .. H.short(place.region, math.floor(width / (H.font(9) * 0.8))),
    }
    if not w.current or w.status == "expired" then
        lines[#lines + 1] =
            "\n${color6}Clima no disponible\n${color3}Reintentando en segundo plano.\n\n${font Ubuntu Sans Mono:size=8}Fuente: Open-Meteo${font}"
        return table.concat(lines, "\n")
    end
    local c = w.current
    local label, glyph = condition(c.weather_code, c.is_day)
    lines[#lines + 1] = "${voffset 4}${color2}${font FontAwesome:size=23}"
        .. glyph
        .. "${font Ubuntu Sans Mono:style=Bold:size=26}${color1} "
        .. number(c.temperature_2m, "%.1f")
        .. " C${font}"
    lines[#lines + 1] = "${font Ubuntu Sans Mono:size=9}${color}"
        .. label
        .. "${alignr}${font Ubuntu Sans Mono:size=8}${color3}"
        .. number(c.wind_speed_10m)
        .. " km/h"
    lines[#lines + 1] = "${font Ubuntu Sans Mono:size=8}${color3}Sensacion "
        .. number(c.apparent_temperature)
        .. " C / Humedad "
        .. number(c.relative_humidity_2m)
        .. "%"
    lines[#lines + 1] =
        "${voffset 2}${color2}${font Ubuntu Sans Mono:style=Bold:size=8}7 DIAS   MIN / MAX${alignr}LLUVIA"
    local weekdays = { "DOM", "LUN", "MAR", "MIE", "JUE", "VIE", "SAB" }
    for _, day in ipairs(w.days or {}) do
        if day.date >= (w.local_date or "") then
            local year, month, date = day.date:match("(%d+)-(%d+)-(%d+)")
            local stamp = os.time({
                year = tonumber(year),
                month = tonumber(month),
                day = tonumber(date),
                hour = 12,
            })
            local name = day.date == w.local_date and "HOY"
                or weekdays[tonumber(os.date("%w", stamp)) + 1]
            local _, icon = condition(day.weather_code, 1)
            lines[#lines + 1] = "${font Ubuntu Sans Mono:size=9}${color}"
                .. name
                .. " ${color2}${font FontAwesome:size=9}"
                .. icon
                .. "${font Ubuntu Sans Mono:size=9} ${color5}"
                .. number(day.temperature_2m_min)
                .. "${color3} / ${color1}"
                .. number(day.temperature_2m_max)
                .. " C${alignr}${color2}"
                .. number(day.precipitation_probability_max)
                .. "%"
        end
    end
    local today = (w.days or {})[1] or {}
    local sunrise = tostring(today.sunrise or ""):match("T(%d%d:%d%d)") or "--:--"
    local sunset = tostring(today.sunset or ""):match("T(%d%d:%d%d)") or "--:--"
    lines[#lines + 1] = "${voffset 2}${font Ubuntu Sans Mono:size=8}${color3}Sol "
        .. sunrise
        .. " / "
        .. sunset
    lines[#lines + 1] = "${font Ubuntu Sans Mono:size=7}"
        .. (w.status == "cached" and "${color6}CACHE / " or "${color3}")
        .. "Open-Meteo / CC BY 4.0 / "
        .. clean(w.updated_time or "--:--")
        .. "${font}"
    return table.concat(lines, "\n")
end
function conky_calendar(width)
    local c = data().calendar or {}
    if not c.month then
        return ""
    end
    local months = {
        "ENERO",
        "FEBRERO",
        "MARZO",
        "ABRIL",
        "MAYO",
        "JUNIO",
        "JULIO",
        "AGOSTO",
        "SEPTIEMBRE",
        "OCTUBRE",
        "NOVIEMBRE",
        "DICIEMBRE",
    }
    local cell = (tonumber(width) or 244) / 7
    local week_count = math.max(1, #c.weeks)
    local base_height = 102 + 18 * week_count
    local card = (H.ui.cards or {}).calendar or {}
    local height = (card.height or base_height * (H.ui.scale or 1)) / (H.ui.scale or 1)
    -- Distribute the extra column height between weeks; H.style scales offsets once.
    local row_gap = math.floor(math.max(0, height - base_height) / week_count)
    local out = {
        "${font Ubuntu Sans Mono:style=Bold:size=12}${color}" .. months[c.month] .. " " .. c.year,
    }
    local headings = {}
    for column, label in ipairs({ "L", "M", "X", "J", "V", "S", "D" }) do
        -- goto is window-relative; include the same 14 px inset as plain text.
        headings[#headings + 1] = "${goto "
            .. ((H.ui.padding or 14) + math.floor((column - 0.5) * cell - H.font(9) * 0.4))
            .. "}"
            .. label
    end
    out[#out + 1] = "${font Ubuntu Sans Mono:size=9}${color3}" .. table.concat(headings)
    for _, week in ipairs(c.weeks) do
        local line = {}
        for column, day in ipairs(week) do
            if day ~= 0 then
                line[#line + 1] = "${goto "
                    .. ((H.ui.padding or 14) + math.floor((column - 0.5) * cell - H.font(11) * 0.8))
                    .. "}"
                    .. (day == c.day and "${color1}${font Ubuntu Sans Mono:style=Bold:size=11}" or "${color3}${font Ubuntu Sans Mono:size=11}")
                    .. string.format("%2d", day)
            end
        end
        out[#out + 1] = "${voffset " .. row_gap .. "}" .. table.concat(line)
    end
    return table.concat(out, "\n") .. "${font}"
end

-- Scale each callback once, after optional facts and sections are assembled.
dofile(os.getenv("CORTEX_NEO_THEME_DIR") .. "/panels.lua")(H)
for name, callback in pairs(_G) do
    if type(callback) == "function" and name:match("^conky_") then
        _G[name] = function(...)
            local value = callback(...)
            return type(value) == "string" and H.style(value) or value
        end
    end
end
