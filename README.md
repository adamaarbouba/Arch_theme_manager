# Arch Theme Manager

A modular theme orchestrator for **Arch Linux + Hyprland**.

Arch Theme Manager applies a single theme across multiple desktop components from one unified theme manifest.

## Preview

### Orbital

<p align="center">
  <img src="assets/demo.png" alt="Orbital desktop preview" width="900">
</p>

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

Run the installer:

```bash
./scripts/install.sh
```

Reload Zsh:

```bash
source ~/.zshrc
```

Verify the installation:

```bash
which themectl
themectl current
themectl doctor
```

The CLI is installed at:

```text
~/.local/bin/themectl
```

## Usage

List installed themes:

```bash
themectl list
```

Show a resolved theme:

```bash
themectl show portal
```

Validate a theme:

```bash
themectl validate portal
```

Apply a theme:

```bash
themectl apply portal
```

Show the current theme:

```bash
themectl current
```

Cycle through themes:

```bash
themectl next
themectl previous
```

Check the installation:

```bash
themectl doctor
```

## Theme Structure

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

A public example theme is included at:

```text
themes/example/
```

## Project Paths

```text
Themes:
~/.config/arch-theme-manager/themes/

Generated:
~/.config/arch-theme-manager/generated/

State:
~/.local/state/arch-theme-manager/

Application:
~/.local/share/arch-theme-manager/

CLI:
~/.local/bin/themectl
```

## Development

Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install development dependencies:

```bash
pip install -e ".[dev]"
```

Run the test suite:

```bash
pytest
```

The project currently includes **45 automated tests** covering loading, inheritance, validation, state, XDG paths, orchestration, rollback behavior, CLI availability, and the bundled example theme.

## Documentation

- `docs/installation.md`
- `docs/themes.md`
- `docs/architecture.md`

## License

MIT
