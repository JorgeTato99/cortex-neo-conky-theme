"""Complete dark palettes inspired by the ten Ubuntu 26 accent choices.

Foregrounds are deliberately brighter than Ubuntu's solid button backgrounds.
All roles are explicit so changing hue never leaves a blue graph behind.
"""

ROLES = ("text", "primary", "secondary", "muted", "border", "accent", "warning", "graph", "background")
_ROWS = {
    "blue": ("DAE9FC", "55AEFF", "6DE4EF", "91A7C2", "265A7C", "B3A1FF", "FFC979", "183451", "081220"),
    "teal": ("DDF7F4", "56D6CE", "8AF0DC", "95B9B5", "286760", "A4BFFF", "FFCF86", "173F3E", "081B1C"),
    "green": ("E6F5DF", "96D56C", "C0E9A0", "A0B593", "426332", "81D5C6", "FFD087", "2A4023", "111C0D"),
    "yellow": ("FFF3D6", "F3CC61", "FFE5A0", "BAAF8E", "76602D", "A4DDBA", "FFA18A", "493C1C", "211B09"),
    "orange": ("FFF0E5", "FFAB75", "FFD1A1", "BEA390", "805035", "E6B2EA", "FFE08A", "4E3021", "22140D"),
    "red": ("FFE7EC", "FF8097", "FFB1BE", "C29BA5", "7B3448", "D2AEFF", "FFDA8D", "4C2431", "220D16"),
    "pink": ("FCE7FC", "E896E8", "FFC2F4", "BA9CBB", "713B72", "A9C8FF", "FFD28C", "452547", "1F1022"),
    "purple": ("EEE8FF", "B3A1FF", "D7C5FF", "A79EBD", "51457F", "91DCEB", "FFD38F", "302A4C", "151022"),
    "slate": ("E7F0EB", "A7C8B2", "D0E5D6", "9CACAA", "49645B", "B9C4EC", "EAD29A", "2B3D37", "111B18"),
    "brown": ("F9EFE1", "DDBA8D", "F2D8B8", "B7A590", "725D42", "B9D0C4", "F3CF85", "453825", "201A10"),
}
PALETTES = {name: dict(zip(ROLES, values, strict=True)) for name, values in _ROWS.items()}
# Read old configurations without resetting unrelated personal choices.
ALIASES = {"neon": "blue", "amber": "yellow", "contrast": "blue"}
