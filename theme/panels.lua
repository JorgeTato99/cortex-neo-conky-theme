-- Content-aware blocks: absent facts do not become labels or empty sections.
return function(H)
    local data = H.data
    local legacy_groups =
        { Aplicaciones = "Applications", Lenguajes = "Languages", Herramientas = "Tools" }
    local function hardware_lines(value, width, size, color)
        local lines = {}
        for _, line in ipairs(H.wrap(value, width, size, 2)) do
            lines[#lines + 1] = "${font Ubuntu Sans Mono:size="
                .. size
                .. "}${"
                .. color
                .. "}"
                .. line
        end
        return lines
    end

    function conky_has(path)
        return H.fresh() and type(H.get(path)) == "number" and "1" or "0"
    end

    function conky_status()
        if H.private_mode() then
            return H.t("${color5}Presentation")
        end
        return H.fresh() and H.t("${color2}Live") or H.t("${color6}Stale")
    end

    function conky_system_meta(width)
        width = tonumber(width) or 244
        local osinfo = data().os or {}
        local lines = hardware_lines(osinfo.name, width, 12, "color")
        for index, line in ipairs(lines) do
            lines[index] = line:gsub(":size=12", ":style=Bold:size=12")
        end
        local subtitle = {}
        for _, key in ipairs({ "codename", "arch" }) do
            if osinfo[key] and osinfo[key] ~= "" then
                subtitle[#subtitle + 1] = H.clean(osinfo[key])
            end
        end
        if #subtitle > 0 then
            lines[#lines + 1] = "${font}${color3}" .. table.concat(subtitle, " / ")
        end
        local details = {
            data().hostname,
            osinfo.kernel and ("Kernel " .. osinfo.kernel),
            osinfo.signature,
            osinfo.compiled,
        }
        if
            H.private_mode()
            or not H.detailed()
            or H.ui.density == "comfortable"
            or H.ui.presentation_profile == "compact"
        then
            details = { osinfo.kernel and ("Kernel " .. osinfo.kernel) }
        end
        for _, value in ipairs(details) do
            if value and value ~= "" then
                for _, line in ipairs(H.wrap(value, width, 7, 2)) do
                    lines[#lines + 1] = "${font Ubuntu Sans Mono:size=7}${color3}" .. line
                end
            end
        end
        return table.concat(lines, "\n") .. "${font}"
    end

    function conky_cpu_meta(width)
        width = tonumber(width) or 292
        local hardware = data().hardware or {}
        local lines = hardware_lines(hardware.cpu_model, width, 9, "color")
        if H.detailed() and hardware.cpu_topology and hardware.cpu_topology ~= "" then
            lines[#lines + 1] = "${font}${color3}" .. H.clean(hardware.cpu_topology)
        end
        return table.concat(lines, "\n") .. "${font}"
    end

    function conky_ram_meta(width)
        width = tonumber(width) or 292
        local hardware = data().hardware or {}
        local lines = hardware_lines(hardware.ram_model, width, 10, "color")
        local subtitle = {}
        for _, key in ipairs(H.detailed() and { "ram_type", "ram_capacity" } or {}) do
            local value = hardware[key]
            if value and value ~= "" and value ~= "N/D" then
                subtitle[#subtitle + 1] = H.clean(value)
            end
        end
        if #subtitle > 0 then
            lines[#lines + 1] = "${color3}" .. table.concat(subtitle, " / ")
        end
        if
            H.detailed()
            and hardware.ram_speed
            and hardware.ram_speed ~= ""
            and hardware.ram_speed ~= "N/D"
        then
            lines[#lines + 1] = H.t("${color3}Configured: ") .. H.clean(hardware.ram_speed)
        end
        return table.concat(lines, "\n") .. "${font}"
    end

    function conky_cpu_top()
        if H.private_mode() then
            return H.t("${color3}Processes hidden")
        end
        local processes = (data().cpu or {}).top or {}
        if not H.fresh() or #processes == 0 then
            return ""
        end
        local limit = H.ui.top_count or 5
        local out = { "${color2}TOP " .. limit .. H.t(" PROCESSES${alignr}${color3}%CPU") }
        local threads = tonumber((data().hardware or {}).cpu_threads) or 1
        for index, process in ipairs(processes) do
            if index > limit then
                break
            end
            out[#out + 1] = "${color}"
                .. H.short(process.name, 18)
                .. "${alignr}${color1}"
                .. string.format("%.2f%%", (process.percent or 0) / threads)
        end
        return table.concat(out, "\n")
    end

    function conky_gpu_meta(width)
        local gpu = data().gpu or {}
        local lines = hardware_lines(gpu.model, tonumber(width) or 292, 10, "color")
        if H.detailed() and gpu.maker and gpu.maker ~= "" then
            lines[#lines + 1] = "${font Ubuntu Sans Mono:size=7}${color3}" .. H.clean(gpu.maker)
        end
        if H.detailed() and gpu.driver and gpu.driver ~= "" then
            lines[#lines + 1] = "${font Ubuntu Sans Mono:size=7}${color3}Driver "
                .. H.clean(gpu.driver)
        end
        return table.concat(lines, "\n") .. "${font}"
    end

    function conky_gpu_summary()
        if not H.fresh() then
            return H.t("${color6}Stale data")
        end
        local gpu = data().gpu or {}
        local text = ""
        if type(gpu.load) == "number" then
            text = "${color1}GPU " .. string.format("%.1f%%", gpu.load)
        elseif type(gpu.frequency) == "number" then
            text = H.t("${color1}Frequency ") .. string.format("%.0f MHz", gpu.frequency)
            if type(gpu.frequency_max) == "number" and gpu.frequency_max > 0 then
                text = text
                    .. H.t("${alignr}${color3}max ")
                    .. string.format("%.0f MHz", gpu.frequency_max)
            end
        end
        if type(gpu.temperature) == "number" then
            text = text .. "${alignr}${color3}" .. string.format("%.0f C", gpu.temperature)
        end
        return text
    end

    function conky_memory_top()
        if H.private_mode() then
            return H.t("${color3}Applications hidden · shared RSS")
        end
        local rows = (data().ram or {}).top or {}
        if not H.fresh() or #rows == 0 then
            return ""
        end
        local limit = H.ui.top_count or 5
        local out = { "${color2}TOP " .. limit .. H.t(" / APPLICATIONS${alignr}${color3}RSS") }
        for index, app in ipairs(rows) do
            if index > limit then
                break
            end
            local rss = tonumber(app.rss) or 0
            local amount = rss >= 1024 ^ 3 and string.format("%.2f GiB", rss / 1024 ^ 3)
                or string.format("%.0f MiB", rss / 1024 ^ 2)
            out[#out + 1] = "${font Ubuntu Sans Mono:size=9}${color}"
                .. H.short(app.name, app.scope == "virtual-machine" and 16 or 21)
                .. (app.scope == "virtual-machine" and " [VM]" or "")
                .. "${alignr}${color1}"
                .. amount
        end
        local ram = data().ram or {}
        local pressure = ((ram.pressure or {}).some or {}).avg10
        local swap = (ram.swap or {}).used
        local psi_text = type(pressure) == "number" and string.format("%.1f%%", pressure) or "—"
        local swap_text = type(swap) == "number" and string.format("%.1fG", swap / 1024 ^ 3)
            or "—"
        out[#out + 1] = H.t("${font Ubuntu Sans Mono:size=7}${color3}Shared RSS · PSI ")
            .. psi_text
            .. " · swap "
            .. swap_text
            .. "${font}"
        return table.concat(out, "\n")
    end

    function conky_disk_summary()
        if not H.fresh() then
            return H.t("Stale data")
        end
        local mounted, unmounted = 0, 0
        for _, disk in ipairs(data().disks or {}) do
            if disk.target or #(disk.mounts or {}) > 0 then
                mounted = mounted + 1
            else
                unmounted = unmounted + 1
            end
        end
        return mounted
            .. (mounted == 1 and H.t(" mounted / ") or H.t(" mounted / "))
            .. unmounted
            .. H.t(" unmounted")
    end

    function conky_other_disks(requested_page)
        local disks = data().disks or {}
        if #disks < 2 then
            return ""
        end
        local card = (H.ui.cards or {}).storage or { height = 248 }
        local budget = card.height - H.pixels(180)
        local pages, height = { {} }, 0
        for index = 2, #disks do
            local disk = disks[index]
            local size = (disk.size or 0) >= 1e12 and string.format("%.1f TB", disk.size / 1e12)
                or string.format("%.0f GB", (disk.size or 0) / 1e9)
            local block = {}
            if disk.target or #(disk.mounts or {}) > 0 then
                local target = H.private_mode() and H.t("mounted") or H.clean(disk.target)
                local state = type(disk.load) == "number"
                        and (target .. " " .. string.format("%.1f%%", disk.load))
                    or H.t("mounted / no reading")
                block = {
                    "${color}" .. H.short(disk.model or disk.name, 44),
                    "${color3}" .. H.clean(disk.kind) .. " / " .. size .. " / " .. state,
                }
            else
                block = {
                    "${color3}" .. H.short(disk.model or disk.name, 20) .. " / " .. size .. H.t(
                        " / unmounted"
                    ),
                }
            end
            local cost = #block * H.font(8) * 1.6
            if height + cost > budget and #pages[#pages] > 0 then
                pages[#pages + 1], height = {}, 0
            end
            for _, line in ipairs(block) do
                pages[#pages][#pages[#pages] + 1] = line
            end
            height = height + cost
        end
        local page = tonumber(requested_page) or (math.floor(os.time() / 30) % #pages + 1)
        page = math.max(1, math.min(#pages, math.floor(page)))
        local out = pages[page]
        if #pages > 1 then
            out[#out + 1] = H.t("${font Ubuntu Sans Mono:size=7}${color3}Disks ")
                .. page
                .. " / "
                .. #pages
        end
        return table.concat(out, "\n")
    end

    function conky_software(requested_page)
        local entries, extra_python = {}, 0
        for _, entry in ipairs(data().software or {}) do
            if
                type(entry) == "table"
                and type(entry.version) == "string"
                and entry.version ~= ""
                and type(entry.label) == "string"
            then
                if entry.family == "python" and entry.role == "additional" then
                    extra_python = extra_python + 1
                else
                    entries[#entries + 1] = entry
                end
            end
        end
        if #entries == 0 then
            return ""
        end
        local card = (H.ui.cards or {}).software or { width = 344, height = 792 }
        local width = card.width - 2 * (H.ui.padding or 14) - H.pixels(10)
        local budget = card.height - 2 * (H.ui.padding or 14) - H.pixels(52)
        local pages = { {} }
        local height, group = 0, ""
        for _, entry in ipairs(entries) do
            local detail = H.wrap(entry.detail or "", width, 9)
            if H.private_mode() or not H.detailed() or H.ui.density == "comfortable" then
                detail = {}
            end
            local note = H.detailed()
                and entry.family == "python"
                and entry.role == "active"
                and extra_python > 0
            local cost = H.font(11) * 1.6
                + H.pixels(6)
                + #detail * H.font(9) * 1.6
                + (note and H.font(8) * 1.6 or 0)
            local category = entry.group or H.t("Applications")
            local heading = category ~= group and H.font(10) * 1.6 + H.pixels(12) or 0
            if height + cost + heading > budget and #pages[#pages] > 0 then
                pages[#pages + 1] = {}
                height, group = 0, ""
                heading = H.font(10) * 1.6 + H.pixels(12)
            end
            pages[#pages][#pages[#pages] + 1] = { entry = entry, detail = detail, note = note }
            height, group = height + cost + heading, category
        end
        local index = tonumber(requested_page) or (math.floor(os.time() / 30) % #pages + 1)
        index = math.max(1, math.min(#pages, math.floor(index)))
        local out = {}
        group = ""
        for _, block in ipairs(pages[index]) do
            local entry = block.entry
            local category = entry.group or H.t("Applications")
            if category ~= group then
                group = category
                out[#out + 1] = "${voffset 12}${font Ubuntu Sans Mono:style=Bold:size=10}${color2}"
                    .. H.t(legacy_groups[category] or H.clean(category)):upper()
            end
            local columns = math.max(
                12,
                math.floor((card.width - 2 * (H.ui.padding or 14)) / (H.font(11) * 0.8))
            )
            local version = H.short(entry.version, math.max(8, math.floor(columns * 0.65)))
            local label =
                H.short(H.t(entry.label), math.max(6, columns - (utf8.len(version) or #version) - 2))
            out[#out + 1] = "${voffset 6}${font Ubuntu Sans Mono:style=Bold:size=11}${color}"
                .. label
                .. "${alignr}${color1}"
                .. version
            for _, line in ipairs(block.detail) do
                out[#out + 1] = "${offset 10}${font Ubuntu Sans Mono:size=9}${color3}" .. line
            end
            if block.note then
                out[#out + 1] = "${offset 10}${font Ubuntu Sans Mono:size=8}${color3}+"
                    .. extra_python
                    .. H.t(" additional versions installed")
            end
        end
        if #pages > 1 then
            out[#out + 1] = H.t("${voffset 4}${font Ubuntu Sans Mono:size=7}${color3}Page ")
                .. index
                .. " / "
                .. #pages
                .. H.t("  -  changes every 30s")
        end
        return table.concat(out, "\n") .. "${font}"
    end
end
