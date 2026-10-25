-- Shared formatting rules. Only renderer-owned strings contain Conky markup.
local M = {}
local cache = os.getenv("CORTEX_NEO_CACHE_DIR") or (os.getenv("HOME") .. "/.cache/cortex-neo")
local ui_file = os.getenv("CORTEX_NEO_UI_FILE") or (cache .. "/ui.lua")
local ok, ui = pcall(dofile, ui_file)
M.ui = ok and type(ui) == "table" and ui or { scale = 1, font_scale = 1, padding = 14, cards = {} }
function M.t(message)
    return (M.ui.translations or {})[message] or message
end
local snapshot, frame = {}, -1
local private_frame, private_value = -1, false

function M.data()
    local current = math.floor(os.time() / 2)
    if current ~= frame then
        local loaded, value = pcall(dofile, cache .. "/dashboard.lua")
        if loaded and type(value) == "table" then
            snapshot = value
        end
        frame = current
    end
    return snapshot
end

function M.private_mode()
    local current = math.floor(os.time() / 2)
    if current == private_frame then
        return private_value
    end
    private_frame = current
    local path = M.ui.presentation_file or os.getenv("CORTEX_NEO_PRESENTATION_FILE")
    if not path or path == "" then
        private_value = (M.data().presentation or {}).enabled == true
        return private_value
    end
    local file, _, code = io.open(path, "r")
    if not file then
        private_value = code ~= 2
        return private_value
    end
    local text = file:read(257) or ""
    file:close()
    local created, expires = text:match("^v1 (%d+) (%d+)%s*$")
    created, expires = tonumber(created), tonumber(expires)
    local valid = created
        and expires
        and #text <= 256
        and created <= os.time() + 5
        and (expires == 0 or (expires > created and expires - created <= 28800))
    private_value = not valid or expires == 0 or os.time() < expires
    return private_value
end

function M.fresh()
    local sampled = M.data().sampled_at
    local age = type(sampled) == "number" and os.time() - sampled or math.huge
    return age >= -5 and age < 10
end

function M.get(path)
    local value = M.data()
    for part in path:gmatch("[^.]+") do
        value = type(value) == "table" and value[tonumber(part) or part] or nil
    end
    return value
end

function M.clean(value)
    if value == nil then
        return ""
    end
    return tostring(value):gsub("[$%c]", " ")
end

function M.font(base)
    return math.max(
        M.ui.min_font_size or 1,
        math.floor(base * (M.ui.font_scale or M.ui.scale or 1) + 0.5)
    )
end

function M.pixels(base)
    return math.floor(base * (M.ui.scale or 1) + 0.5)
end

function M.style(text)
    text = text:gsub("Ubuntu Sans Mono", function()
        return M.ui.font_family or "DejaVu Sans Mono"
    end)
    text = text:gsub("(%${font[^}]-size=)(%d+)", function(prefix, size)
        return prefix .. M.font(tonumber(size))
    end)
    for _, name in ipairs({ "offset", "voffset" }) do
        text = text:gsub("(%${" .. name .. "%s+)(%-?%d+)", function(prefix, value)
            return prefix .. M.pixels(tonumber(value))
        end)
    end
    return text
end

function M.detailed()
    return M.ui.detail_level ~= "essential"
end

function M.short(text, length)
    text = M.clean(text)
    local count = utf8.len(text) or #text
    if count <= length then
        return text
    end
    local end_byte = utf8.offset(text, length - 1) or length
    return text:sub(1, end_byte - 1) .. "…"
end

function M.wrap(text, width, size, limit)
    local count = math.max(12, math.floor(width / (M.font(size) * 0.8)))
    local lines, line = {}, ""
    for word in M.clean(text):gmatch("%S+") do
        -- Long commit hashes and model identifiers have no spaces to wrap at.
        while (utf8.len(word) or #word) > count do
            if line ~= "" then
                lines[#lines + 1], line = line, ""
            end
            local cut = utf8.offset(word, count + 1) or (#word + 1)
            lines[#lines + 1], word = word:sub(1, cut - 1), word:sub(cut)
        end
        if (utf8.len(line) or #line) + (utf8.len(word) or #word) + 1 > count and line ~= "" then
            lines[#lines + 1] = line
            line = word
        else
            line = line == "" and word or line .. " " .. word
        end
    end
    if line ~= "" then
        lines[#lines + 1] = line
    end
    if limit and #lines > limit then
        while #lines > limit do
            table.remove(lines)
        end
        lines[limit] = M.short(lines[limit], count - 1) .. "…"
    end
    return lines
end

function M.bytes(value)
    if type(value) ~= "number" then
        return "—"
    end
    return string.format("%.1f GiB", value / 1024 ^ 3)
end

return M
