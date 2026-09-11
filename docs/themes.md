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

Colors use hexadecimal notation:

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

Shared settings can be placed in a base theme directory whose name begins with `_`.

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

Directories beginning with `_` are internal themes and are not included in normal theme rotation.

## Listing Themes

```bash
themectl list
```

The active theme is marked with `*`.

## Showing a Theme

Show the fully resolved configuration:

```bash
themectl show portal
```

Inherited values are already merged in the output.

## Validating a Theme

```bash
themectl validate portal
```

Validation checks the theme before it is applied.

## Applying a Theme

```bash
themectl apply portal
```

## Current Theme

```bash
themectl current
```

## Theme Rotation

Move to the next theme:

```bash
themectl next
```

Move to the previous theme:

```bash
themectl previous
```

Theme rotation automatically uses the currently installed themes.

## Installing a Theme

Install a theme from a directory:

```bash
themectl install-theme /path/to/theme
```

The directory name is used as the installed theme name by default.

Example:

```bash
themectl install-theme ~/Downloads/my-theme
```

Install it using a different name:

```bash
themectl install-theme \
    ~/Downloads/my-theme \
    --name portal
```

If a theme with that name already exists, installation is refused.

To replace an existing theme:

```bash
themectl install-theme \
    ~/Downloads/my-theme \
    --name portal \
    --force
```

Themes are validated before installation is completed.

A failed installation does not leave a partially installed theme behind.

## Removing a Theme

Remove an installed theme:

```bash
themectl remove-theme portal
```

The currently active theme is protected and cannot normally be removed.

If removal of the active theme is intentional:

```bash
themectl remove-theme portal --force
```

Forced removal of the current theme also clears the current theme state.

Internal themes such as `_base` cannot be removed through `remove-theme`.

Symlinked theme directories are also refused for safety.

## Renaming a Theme

Rename an installed theme:

```bash
themectl rename-theme portal gateway
```

This changes:

```text
theme directory name
theme.json name field
current theme state
previous theme state
```

when those state values reference the renamed theme.

The command refuses to overwrite an existing theme.

Example:

```bash
themectl rename-theme orbital space
```

Afterward:

```bash
themectl list
```

will show:

```text
space
```

instead of:

```text
orbital
```

Internal themes beginning with `_` cannot be renamed.

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

Or use the installer:

```bash
themectl install-theme \
    themes/example \
    --name my-theme
```

Validate it:

```bash
themectl validate my-theme
```

Apply it:

```bash
themectl apply my-theme
```

## Theme Management Workflow

A typical workflow is:

```bash
themectl install-theme /path/to/theme --name new-theme
themectl validate new-theme
themectl apply new-theme
themectl rename-theme new-theme final-name
themectl remove-theme final-name
```

Use:

```bash
themectl doctor
```

at any time to check the health of the theme manager and its desktop integrations.
