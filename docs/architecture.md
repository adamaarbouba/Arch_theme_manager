# Architecture

Arch Theme Manager separates theme data, validation, orchestration, state, and desktop-specific integrations.

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

The loader is responsible for:

- discovering installed themes
- reading `theme.json`
- resolving inheritance
- deep-merging inherited values
- detecting circular inheritance
- attaching internal metadata such as the theme directory

Theme directories beginning with `_` are treated as internal base themes and are not included in normal theme rotation.

## Validator

The validator checks a resolved theme before anything is applied.

It validates:

- required colors
- hexadecimal color format
- wallpaper configuration
- Hyprpaper settings
- window rounding
- rounding power
- opacity
- border size
- monitor type

Validation happens before desktop state is modified.

## Orchestrator

The orchestrator coordinates theme application.

The normal flow is:

```text
load
  ↓
validate
  ↓
apply adapters
  ↓
save state
```

State is saved only after a successful theme application.

If an adapter fails, the orchestrator attempts a compensating rollback by re-applying the previously active theme.

This is not a fully atomic desktop transaction, because external programs are changed independently, but it provides recovery from partial application failures.

## Adapters

Each supported desktop component has its own adapter.

### Hyprpaper

Updates the active wallpaper.

### Waybar

Generates:

```text
waybar-theme.css
```

Then reloads Waybar.

### SwayNC

Generates:

```text
swaync-theme.css
```

Then reloads SwayNC CSS.

### Hyprland

Generates:

```text
hyprland-theme.lua
```

The generated file controls settings such as:

- border colors
- border size
- rounding
- opacity
- shadow color

Hyprland is reloaded after generation.

### Kitty

Generates:

```text
kitty-theme.conf
```

Existing Kitty instances are updated through Kitty remote control sockets.

### Zsh

Generates:

```text
zsh-theme.zsh
```

Interactive Zsh shells register their process IDs in the runtime directory.

After a theme change, the adapter sends `SIGUSR1` to registered Zsh processes so they can reload the prompt immediately.

### Hyprlock

Generates:

```text
hyprlock-theme.conf
```

This includes theme colors and the resolved wallpaper path.

### Hyprtoolkit

Generates:

```text
hyprtoolkit-theme.conf
```

Hyprlauncher is restarted so the new toolkit colors become active.

## Generated Files

Generated configuration fragments are stored in:

```text
~/.config/arch-theme-manager/generated/
```

Desktop applications reference these files using stable symlinks or configuration includes.

## Theme Storage

User themes are stored in:

```text
~/.config/arch-theme-manager/themes/
```

## State

Persistent theme state is stored in:

```text
~/.local/state/arch-theme-manager/current.json
```

The state tracks:

```text
current
previous
```

This supports commands such as:

```bash
themectl current
themectl previous
```

## Runtime State

Temporary process information is stored under:

```text
$XDG_RUNTIME_DIR/arch-theme-manager/
```

If `XDG_RUNTIME_DIR` is unavailable, the fallback is:

```text
/tmp/arch-theme-manager-UID/
```

For example, registered Zsh processes live under:

```text
$XDG_RUNTIME_DIR/arch-theme-manager/zsh/
```

## XDG Layout

Arch Theme Manager uses:

```text
Configuration:
~/.config/arch-theme-manager/

State:
~/.local/state/arch-theme-manager/

Application installation:
~/.local/share/arch-theme-manager/

CLI:
~/.local/bin/themectl
```

## CLI

The CLI is exposed through:

```text
themectl
```

Supported commands:

```bash
themectl list
themectl show THEME
themectl validate THEME
themectl apply THEME
themectl current
themectl next
themectl previous
themectl doctor
```

## Doctor

`themectl doctor` checks:

- installed themes
- theme validity
- current state
- required commands
- running processes
- generated files
- integration symlinks
- configuration includes
- Hyprland IPC
- Hyprland configuration errors
