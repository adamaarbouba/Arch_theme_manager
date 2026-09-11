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

Directories beginning with `_` are internal themes and are not included in normal theme rotation.

## Listing Themes

```bash
themectl list
```

The active theme is marked with `*`.

## Showing a Theme

```bash
themectl show portal
```

This shows the fully resolved theme configuration, including inherited values.

## Validating a Theme

```bash
themectl validate portal
```

Validation occurs before a theme is applied or installed.

## Applying a Theme

```bash
themectl apply portal
```

## Current Theme

```bash
themectl current
```

## Theme Rotation

Next theme:

```bash
themectl next
```

Previous theme:

```bash
themectl previous
```

Theme rotation automatically uses the currently installed themes.

## Installing a Theme

Install a theme directory:

```bash
themectl install-theme /path/to/theme
```

Install using a custom name:

```bash
themectl install-theme \
    /path/to/theme \
    --name portal
```

Replace an existing theme:

```bash
themectl install-theme \
    /path/to/theme \
    --name portal \
    --force
```

Themes are validated before installation completes.

Failed installations do not leave partially installed themes behind.

## Copying a Theme

Duplicate an existing installed theme:

```bash
themectl copy-theme portal portal-copy
```

The source remains unchanged.

The copied theme receives:

```text
a new directory
a copied wallpaper
a copied manifest
an updated name field
```

For example:

```bash
themectl copy-theme orbital orbital-edit
```

Now both themes exist:

```text
orbital/
orbital-edit/
```

You can edit:

```text
~/.config/arch-theme-manager/themes/orbital-edit/theme.json
```

without modifying the original `orbital` theme.

The copy is validated before installation is completed.

If validation fails, the copied theme is not installed and temporary staging files are cleaned up.

Internal themes such as `_base` cannot be copied through `copy-theme`.

Symlinked source themes are refused for safety.

## Renaming a Theme

Rename an installed theme:

```bash
themectl rename-theme portal gateway
```

This updates:

```text
theme directory name
theme.json name field
current theme state
previous theme state
```

when applicable.

The command refuses to overwrite an existing theme.

Internal themes cannot be renamed.

## Removing a Theme

Remove an installed theme:

```bash
themectl remove-theme portal
```

The active theme is protected.

To intentionally remove the active theme:

```bash
themectl remove-theme portal --force
```

Forced removal clears the active theme state.

Internal themes and symlinked themes are protected from removal.

## Creating a Theme

A simple starting point is the bundled example:

```bash
themectl install-theme \
    themes/example \
    --name my-theme
```

Or copy an existing installed theme:

```bash
themectl copy-theme \
    orbital \
    my-theme
```

Then edit:

```text
~/.config/arch-theme-manager/themes/my-theme/theme.json
```

Validate:

```bash
themectl validate my-theme
```

Apply:

```bash
themectl apply my-theme
```

## Theme Management Workflow

Example workflow:

```bash
themectl install-theme themes/example --name base-custom
themectl copy-theme base-custom experiment
themectl validate experiment
themectl apply experiment
themectl rename-theme experiment finished-theme
themectl remove-theme finished-theme
```

Use:

```bash
themectl doctor
```

at any time to inspect the health of Arch Theme Manager and its desktop integrations.
