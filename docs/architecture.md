# Architecture

Arch Theme Manager separates theme data, validation, orchestration, state, theme management, and desktop-specific integrations.

## High-Level Flow

```text
theme.json
    │
    ▼
ThemeLoader
    │
    ▼
ThemeValidator
    │
    ▼
ThemeOrchestrator
    │
    ├── HyprpaperAdapter
    ├── WaybarAdapter
    ├── SwayNCAdapter
    ├── HyprlandAdapter
    ├── KittyAdapter
    ├── ZshAdapter
    ├── HyprlockAdapter
    └── HyprtoolkitAdapter
```

## Loader

The loader handles:

```text
theme discovery
manifest loading
inheritance
deep merging
circular inheritance detection
resolved theme metadata
```

Theme directories beginning with `_` are treated as internal base themes and are excluded from normal rotation.

## Validator

Themes are validated before desktop state is modified.

Validation includes:

```text
required colors
hexadecimal color values
wallpaper settings
Hyprpaper configuration
window rounding
rounding power
opacity
border size
monitor type
```

## Orchestrator

Normal application flow:

```text
load
  ↓
validate
  ↓
apply adapters
  ↓
save state
```

State is written only after a successful application.

If an adapter fails, the orchestrator attempts a compensating rollback using the previously active theme.

This is not a fully atomic desktop transaction because external desktop programs are modified independently.

## Theme Management

Theme management is separated from theme application.

### ThemeInstaller

Installs a theme from an external directory.

It uses a temporary staging directory, validates the copied theme, then moves it into the final theme directory.

### ThemeCopier

Duplicates an existing installed theme.

It:

```text
copies the source into staging
updates the manifest name
validates the copied theme
moves the copy into its final directory
cleans failed staging data
```

### ThemeRenamer

Renames an installed theme and updates its manifest.

If the renamed theme appears in persistent state, the current or previous theme reference is updated.

### ThemeRemover

Removes installed themes.

The currently active theme is protected unless forced removal is requested.

Forced removal of the active theme clears persistent theme state.

## Adapters

### Hyprpaper

Updates the active wallpaper.

### Waybar

Generates:

```text
waybar-theme.css
```

and reloads Waybar.

### SwayNC

Generates:

```text
swaync-theme.css
```

and reloads SwayNC CSS.

### Hyprland

Generates:

```text
hyprland-theme.lua
```

It controls settings such as border colors, border size, rounding, opacity, and shadow color.

### Kitty

Generates:

```text
kitty-theme.conf
```

Existing Kitty instances are updated through remote-control sockets.

### Zsh

Generates:

```text
zsh-theme.zsh
```

Interactive Zsh processes register themselves in the runtime directory.

Theme changes signal registered shells with `SIGUSR1`, allowing prompt colors to update immediately.

### Hyprlock

Generates:

```text
hyprlock-theme.conf
```

This contains theme colors and the resolved wallpaper path.

### Hyprtoolkit

Generates:

```text
hyprtoolkit-theme.conf
```

Hyprlauncher is restarted after changes so the new colors become active.

## Generated Files

Generated files are stored under:

```text
~/.config/arch-theme-manager/generated/
```

Desktop applications reference them through stable symlinks or configuration includes.

## Theme Storage

Installed themes live at:

```text
~/.config/arch-theme-manager/themes/
```

## State

Persistent state lives at:

```text
~/.local/state/arch-theme-manager/current.json
```

It stores:

```text
current
previous
```

## Runtime State

Transient runtime information lives under:

```text
$XDG_RUNTIME_DIR/arch-theme-manager/
```

Fallback:

```text
/tmp/arch-theme-manager-UID/
```

Registered Zsh shells are stored under:

```text
$XDG_RUNTIME_DIR/arch-theme-manager/zsh/
```

## XDG Layout

```text
Configuration:
~/.config/arch-theme-manager/

State:
~/.local/state/arch-theme-manager/

Application:
~/.local/share/arch-theme-manager/

CLI:
~/.local/bin/themectl
```

## CLI

Theme application commands:

```bash
themectl list
themectl show THEME
themectl validate THEME
themectl apply THEME
themectl current
themectl next
themectl previous
```

Theme management commands:

```bash
themectl install-theme PATH
themectl copy-theme SOURCE NEW_NAME
themectl rename-theme OLD_NAME NEW_NAME
themectl remove-theme THEME
```

System health:

```bash
themectl doctor
```

## Doctor

`themectl doctor` checks:

```text
installed themes
theme validity
current state
required commands
running processes
generated files
integration symlinks
configuration includes
Hyprland IPC
Hyprland configuration errors
```
