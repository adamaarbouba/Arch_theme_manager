# Themes

Themes are stored in:

```text
~/.config/arch-theme-manager/themes/
```

Each theme is a directory containing a `theme.json` manifest and a wallpaper.

Example:

```text
portal/
├── theme.json
└── wallpaper.png
```

## Theme Manifest

Example:

```json
{
  "name": "example",
  "wallpaper": "wallpaper.png",

  "colors": {
    "background": "#111827",
    "surface": "#1F2937",
    "foreground": "#F9FAFB",
    "primary": "#8B5CF6",
    "secondary": "#38BDF8",
    "accent": "#F472B6"
  },

  "hyprpaper": {
    "fit_mode": "cover"
  },

  "window": {
    "rounding": 10,
    "rounding_power": 2,
    "opacity": 0.96,
    "border_size": 2
  }
}
```

## Required Colors

A theme must define:

```text
background
surface
foreground
primary
secondary
accent
```

Colors use hexadecimal notation such as:

```text
#8B5CF6
```

Eight-digit hexadecimal colors are also supported:

```text
#8B5CF6FF
```

## Wallpaper

The wallpaper path is relative to the theme directory.

Example:

```json
{
  "wallpaper": "wallpaper.png"
}
```

## Hyprpaper

Example:

```json
{
  "hyprpaper": {
    "fit_mode": "cover"
  }
}
```

A monitor can also be specified:

```json
{
  "hyprpaper": {
    "fit_mode": "cover",
    "monitor": "eDP-1"
  }
}
```

## Window Settings

Example:

```json
{
  "window": {
    "rounding": 10,
    "rounding_power": 2,
    "opacity": 0.96,
    "border_size": 2
  }
}
```

## Theme Inheritance

Shared settings can be placed in a base theme directory whose name starts with `_`.

Example:

```text
_base/
└── theme.json
```

A theme can inherit from it:

```json
{
  "extends": "_base"
}
```

Inherited dictionaries are deep-merged.

For example, if `_base` contains:

```json
{
  "window": {
    "rounding": 10,
    "opacity": 0.90
  }
}
```

and the child contains:

```json
{
  "extends": "_base",

  "window": {
    "opacity": 0.96
  }
}
```

the resolved result keeps:

```text
rounding = 10
opacity  = 0.96
```

Directories beginning with `_` are not shown in normal theme rotation.

## Commands

List installed themes:

```bash
themectl list
```

Show the resolved theme:

```bash
themectl show portal
```

Validate:

```bash
themectl validate portal
```

Apply:

```bash
themectl apply portal
```

Show current theme:

```bash
themectl current
```

Switch forward or backward:

```bash
themectl next
themectl previous
```

## Creating a Theme

Copy the bundled example:

```bash
cp -r \
    themes/example \
    ~/.config/arch-theme-manager/themes/my-theme
```

Then edit:

```text
~/.config/arch-theme-manager/themes/my-theme/theme.json
```

Validate before applying:

```bash
themectl validate my-theme
```
