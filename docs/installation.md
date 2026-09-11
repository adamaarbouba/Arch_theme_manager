# Installation

Arch Theme Manager is designed for Arch Linux with Hyprland.

## Supported Integrations

The manager currently supports:

- Hyprland
- Hyprpaper
- Waybar
- SwayNC
- Kitty
- Zsh
- Hyprlock
- Hyprlauncher / Hyprtoolkit

## Install

Clone the repository:

```bash
git clone https://github.com/adamaarbouba/Arch_theme_manager.git
cd Arch_theme_manager
```

Run the installer:

```bash
./scripts/install.sh
```

The installer creates its own Python environment at:

```text
~/.local/share/arch-theme-manager/venv
```

The stable CLI is installed at:

```text
~/.local/bin/themectl
```

Configuration is stored at:

```text
~/.config/arch-theme-manager
```

State is stored at:

```text
~/.local/state/arch-theme-manager
```

After installation, reload Zsh:

```bash
source ~/.zshrc
```

Verify the installation:

```bash
which themectl
themectl current
themectl doctor
```

## Migration

If an older installation exists at:

```text
~/.config/hypr/theme-engine
```

the installer can migrate its themes and desktop integrations.

Existing configuration files are backed up before changes are made.

Do not delete the old theme engine until the migrated installation has been tested successfully.
