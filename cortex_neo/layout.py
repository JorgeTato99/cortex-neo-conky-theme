"""Pure proportional layouts, calculated in GDK application pixels."""

import math

GAP = 16
MARGIN = 20


def visible_cards(snapshot=None, hidden=()):
    if snapshot is None:
        return {
            "system",
            "cpu",
            "ram",
            "gpu",
            "storage",
            "network",
            "software",
            "weather",
            "calendar",
        } - (set(hidden) - {"system"})
    cards = {"system", "cpu", "ram", "calendar"}
    if (snapshot.get("gpu") or {}).get("model"):
        cards.add("gpu")
    if snapshot.get("disks"):
        cards.add("storage")
    if (snapshot.get("network") or {}).get("interface") or snapshot.get("docker_available"):
        cards.add("network")
    if any(isinstance(v, dict) and v.get("version") for v in snapshot.get("software", []) or []):
        cards.add("software")
    if (snapshot.get("weather") or {}).get("location", {}).get("name") and not (
        snapshot.get("presentation") or {}
    ).get("enabled"):
        cards.add("weather")
    return cards - (set(hidden) - {"system"})


def calculate(
    area,
    snapshot=None,
    calendar_weeks=6,
    multiplier=1.0,
    mode="auto",
    *,
    hidden=(),
    anchor="right",
    profile="full",
    density="complete",
):
    """Scale fonts and geometry together, preserving equal hardware row heights.

    The landscape reference is the approved 1304x792 layout. Portrait displays
    use two columns before proportional scaling, avoiding microscopic text.
    The work area already excludes the desktop's dock and top bar.
    """
    ax, ay, aw, ah = area
    if mode not in ("auto", "landscape", "portrait"):
        mode = "auto"
    if not all(math.isfinite(v) for v in area) or aw <= 0 or ah <= 0:
        raise ValueError("Display work area must be finite and positive")
    try:
        multiplier = float(multiplier)
    except (ValueError, TypeError):
        multiplier = 1.0
    if not math.isfinite(multiplier) or not 0.5 <= multiplier <= 1:
        multiplier = 1.0
    active = visible_cards(snapshot, hidden)
    selected = (
        "compact"
        if profile == "compact" or (profile == "auto" and (aw < 1100 or ah < 650))
        else "full"
    )
    comfortable = density == "comfortable"
    if selected == "compact":
        active &= {"system", "cpu", "ram", "gpu", "storage", "network"}
    cards = {}
    heights = dict(
        system=200,
        weather=340,
        calendar=102 + 18 * calendar_weeks,
        cpu=320,
        ram=320,
        gpu=248,
        storage=248,
        network=192,
        software=792,
    )

    def add(name, x, y, w, h=None):
        if name in active:
            cards[name] = dict(x=x, y=y, w=w, h=heights[name] if h is None else h)

    portrait = mode == "portrait" or (mode == "auto" and aw < ah)
    if selected == "compact" and not portrait:
        width = 992
        top = [name for name in ("system", "cpu", "ram") if name in active]
        bottom = [name for name in ("gpu", "storage", "network") if name in active]
        for index, name in enumerate(top):
            add(
                name,
                index * (width + GAP) / len(top),
                0,
                (width - GAP * (len(top) - 1)) / len(top),
                288,
            )
        for index, name in enumerate(bottom):
            add(
                name,
                index * (width + GAP) / len(bottom),
                304,
                (width - GAP * (len(bottom) - 1)) / len(bottom),
                248,
            )
    elif selected == "compact":
        width = 656
        heights.update(system=152, cpu=256, ram=256, gpu=224, storage=224, network=176)
        add("system", 0, 0, width)
        y = heights["system"] + GAP
        for names in [("cpu", "ram"), ("gpu", "storage")]:
            present = [name for name in names if name in active]
            for index, name in enumerate(present):
                add(name, index * 336, y, 320 if len(present) == 2 else width)
            if present:
                y += max(heights[name] for name in present) + GAP
        add("network", 0, y, width)
    elif portrait:
        width = 656
        y = 0
        for names in [
            ("system", "weather"),
            ("cpu", "ram"),
            ("gpu", "storage"),
            ("calendar", "network"),
        ]:
            present = [name for name in names if name in active]
            if not present:
                continue
            for index, name in enumerate(present):
                add(name, index * 336, y, 320 if len(present) == 2 else width)
            y += max(heights[name] for name in present) + GAP
        if "software" in active:
            add("software", 0, y, width)
    else:
        width = 1304 if "software" in active else 944
        y = 0
        for name in ("system", "weather", "calendar"):
            if name in active:
                add(name, 0, y, 272)
                y += heights[name] + GAP
        add("cpu", 288, 0, 320)
        add("ram", 624, 0, 320)
        devices = [name for name in ("gpu", "storage") if name in active]
        for index, name in enumerate(devices):
            add(name, 288 + index * 336, 336, 320 if len(devices) == 2 else 656)
        network_y = 336 + (248 + GAP if devices else 0)
        add("network", 288, network_y, 656)
        add("software", 960, 0, 344)
    height = max(card["y"] + card["h"] for card in cards.values())
    if not portrait and "calendar" in cards:
        # The last card fills its column to the same bottom edge as the dashboard.
        cards["calendar"]["h"] = height - cards["calendar"]["y"]
    scale = min(aw / (width + 2 * MARGIN), ah / (height + 2 * MARGIN)) * multiplier
    for card in cards.values():
        for key in ("x", "y", "w", "h"):
            card[key] *= scale
    return dict(
        x=ax + MARGIN * scale if anchor == "left" else ax + aw - (width + MARGIN) * scale,
        y=ay + MARGIN * scale,
        width=width * scale,
        height=height * scale,
        cards=cards,
        scale=scale,
        gap=GAP * scale,
        margin=MARGIN * scale,
        area=list(area),
        profile="portrait" if portrait else "landscape",
        presentation_profile=selected,
        density="comfortable" if comfortable else "complete",
        min_font_size=9 if comfortable else 7,
        top_count=3 if comfortable or selected == "compact" else 5,
        columns=2
        if portrait
        else (3 if selected == "compact" else (4 if "software" in active else 3)),
    )
