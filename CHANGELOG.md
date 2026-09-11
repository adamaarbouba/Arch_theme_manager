# Changelog

All notable changes to Arch Theme Manager are documented here.

## [Unreleased]

## [0.2.0]

### Added

- `themectl install-theme`
  - Install themes from external directories
  - Custom installed names with `--name`
  - Existing-theme replacement with `--force`
  - Validation before installation
  - Staging-based installation to avoid partial themes

- `themectl copy-theme`
  - Duplicate an installed theme
  - Preserve the original theme
  - Update the copied manifest name
  - Validate copies before installation
  - Clean temporary staging directories after failure

- `themectl rename-theme`
  - Rename installed themes
  - Update the theme manifest name
  - Update current theme state
  - Update previous theme state

- `themectl remove-theme`
  - Remove installed themes
  - Protect the currently active theme
  - Explicit active-theme removal with `--force`
  - Clear persistent state when the active theme is force-removed

- `themectl export-theme`
  - Export installed themes to external directories
  - Validate themes before export
  - Protect existing exports
  - Replace exports with `--force`
  - Staging and backup-based replacement
  - Refuse unsafe symlink replacements

### Documentation

- Expanded theme management documentation
- Added architecture documentation for theme management components
- Added CLI usage examples
- Added export workflow documentation
- Added desktop and doctor screenshots to the README

### Testing

- Added unit tests for theme installation
- Added unit tests for theme copying
- Added unit tests for theme renaming
- Added unit tests for theme removal
- Added unit tests for theme exporting
- Added CLI integration tests for all new management commands

## [0.1.0]

Initial public release.

### Added

- Unified theme manifests
- Theme discovery
- Theme validation
- Theme inheritance
- Deep configuration merging
- Current and previous theme state
- Theme rotation
- Hyprland integration
- Hyprpaper integration
- Waybar integration
- SwayNC integration
- Kitty integration
- Zsh integration
- Hyprlock integration
- Hyprtoolkit integration
- `themectl doctor`
- XDG-compliant application paths
- Migration installer
- Automated test workflow
