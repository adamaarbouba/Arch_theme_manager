# Arch Theme Manager

A modular theme orchestrator for Arch Linux and Hyprland.

One theme switch can coordinate:

- Hyprpaper
- Hyprland
- Waybar
- SwayNC
- Kitty
- Zsh
- Hyprlock
- Hyprtoolkit / Hyprlauncher

## Status

Currently under active development.

The project began as a personal Hyprland theme engine and is being
refactored into a reusable Python package.

## CLI

The primary command is:

```bash
themectl# Arch Theme Manager

A modular theme orchestrator for Arch Linux + Hyprland.

Arch Theme Manager applies a single theme across multiple desktop components from one theme manifest.


## Preview

### Orbital

![Orbital desktop](assets/demo.png)


## Supported Integrations

- Hyprland
- Hyprpaper
- Waybar
- SwayNC
- Kitty
- Zsh
- Hyprlock
- Hyprlauncher / Hyprtoolkit

## Features

- Single theme manifest
- Live theme switching
- Theme inheritance
- Deep configuration merging
- Theme validation
- Current and previous theme state
- Compensating rollback
- XDG-compliant paths
- Integration health checks
- Migration-safe installer
- Automatic next/previous theme rotation

## Installation

Clone the repository:

```bash
git clone https://github.com/adamaarbouba/Arch_theme_manager.git
cd Arch_theme_manager
```

Run:

```bash
./scripts/install.sh
```

Reload Zsh:

```bash
source ~/.zshrc
```

Verify:

```bash
which themectl
themectl current
themectl doctor
```

The CLI should be installed at:

```text
~/.local/bin/themectl
```

## Usage

List themes:

```bash
themectl list
```

Show a resolved theme:

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

Show the current theme:

```bash
themectl current
```

Switch themes:

```bash
themectl next
themectl previous
```

Check system health:

```bash
themectl doctor
```

## Theme Storage

Themes are stored in:

```text
~/.config/arch-theme-manager/themes/
```

Example:

```text
portal/
├── theme.json
└── wallpaper.png
```

A bundled example theme is available in:

```text
themes/example/
```

## Generated Files

Generated configuration fragments are stored in:

```text
~/.config/arch-theme-manager/generated/
```

## State

Persistent state is stored in:

```text
~/.local/state/arch-theme-manager/
```

The manager tracks both the current and previous themes.

## Application Files

The installed application environment lives at:

```text
~/.local/share/arch-theme-manager/
```

## Development

Create a development environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install the package with development dependencies:

```bash
pip install -e ".[dev]"
```

Run tests:

```bash
pytest
```

The core test suite covers:

- theme loading
- inheritance
- deep merging
- validation
- XDG paths
- state handling
- orchestrator behavior
- rollback behavior
- CLI availability
- bundled example theme

## Documentation

More details are available in:

```text
docs/installation.md
docs/themes.md
docs/architecture.md
```

## Migration

Older installations using:

```text
~/.config/hypr/theme-engine
```

can be migrated by the installer.

Existing configuration files are backed up before integration changes are made.

Keep the old installation until the migrated setup has been verified.

## License

MIT
