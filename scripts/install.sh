#!/usr/bin/env bash

set -euo pipefail

# ============================================================
# PROJECT
# ============================================================

PROJECT_DIR="$(
  cd "$(dirname "${BASH_SOURCE[0]}")/.." &&
    pwd
)"

# ============================================================
# PATHS
# ============================================================

CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}"
DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}"
STATE_HOME="${XDG_STATE_HOME:-$HOME/.local/state}"

ATM_CONFIG="$CONFIG_HOME/arch-theme-manager"
ATM_DATA="$DATA_HOME/arch-theme-manager"
ATM_STATE="$STATE_HOME/arch-theme-manager"

ATM_THEMES="$ATM_CONFIG/themes"
ATM_GENERATED="$ATM_CONFIG/generated"
ATM_INTEGRATIONS="$ATM_CONFIG/integrations"

ATM_VENV="$ATM_DATA/venv"

LOCAL_BIN="$HOME/.local/bin"
ATM_BIN="$LOCAL_BIN/themectl"

OLD_ENGINE="$CONFIG_HOME/hypr/theme-engine"

BACKUP_ROOT="$ATM_CONFIG/backups"
BACKUP_DIR="$BACKUP_ROOT/$(date +%Y%m%d-%H%M%S)"

# ============================================================
# OUTPUT
# ============================================================

info() {
  printf '[INFO] %s\n' "$1"
}

ok() {
  printf '[OK]   %s\n' "$1"
}

warn() {
  printf '[WARN] %s\n' "$1"
}

fail() {
  printf '[FAIL] %s\n' "$1" >&2
  exit 1
}

# ============================================================
# FILE HELPERS
# ============================================================

ensure_file() {
  local file="$1"

  mkdir -p "$(dirname "$file")"

  if [[ ! -e "$file" ]]; then
    touch "$file"
  fi
}

backup_file() {
  local file="$1"

  if [[ ! -e "$file" && ! -L "$file" ]]; then
    return
  fi

  local relative
  local destination

  if [[ "$file" == "$HOME/"* ]]; then
    relative="${file#$HOME/}"
  else
    relative="$(basename "$file")"
  fi

  destination="$BACKUP_DIR/$relative"

  mkdir -p "$(dirname "$destination")"

  # Do not back up the same file twice.
  if [[ -e "$destination" || -L "$destination" ]]; then
    return
  fi

  cp -a -- "$file" "$destination"

  ok "Backed up $file"
}

append_once() {
  local file="$1"
  local line="$2"

  ensure_file "$file"

  if grep -Fqx "$line" "$file"; then
    return
  fi

  printf '\n%s\n' "$line" >>"$file"

  ok "Updated $file"
}

prepend_once() {
  local file="$1"
  local line="$2"

  ensure_file "$file"

  if grep -Fqx "$line" "$file"; then
    return
  fi

  local temporary
  temporary="$(mktemp)"

  {
    printf '%s\n\n' "$line"
    cat "$file"
  } >"$temporary"

  cat "$temporary" >"$file"
  rm -f "$temporary"

  ok "Updated $file"
}

ensure_css_theme_import() {
  local file="$1"

  ensure_file "$file"

  if grep -Eq \
    '@import[[:space:]]+(url\()?["'\'']theme\.css["'\'']\)?;' \
    "$file"; then
    return
  fi

  prepend_once \
    "$file" \
    '@import "theme.css";'
}

link_generated() {
  local target="$1"
  local link="$2"

  mkdir -p "$(dirname "$link")"

  if [[ -e "$link" || -L "$link" ]]; then
    backup_file "$link"
    rm -f "$link"
  fi

  ln -s "$target" "$link"

  ok "$link -> $target"
}

# ============================================================
# ZSH MIGRATION
# ============================================================

remove_old_zsh_theme_block() {
  local zshrc="$HOME/.zshrc"

  [[ -f "$zshrc" ]] || return

  if ! grep -Fq \
    'THEME_FILE="$HOME/.config/hypr/theme-engine/generated/zsh-theme.zsh"' \
    "$zshrc"; then
    return
  fi

  info "Removing old inline Zsh theme block"

  python - "$zshrc" <<'PY'
from pathlib import Path
import sys


path = Path(sys.argv[1])

lines = path.read_text(
    encoding="utf-8",
).splitlines(keepends=True)


needle = (
    'THEME_FILE="$HOME/.config/hypr/'
    'theme-engine/generated/zsh-theme.zsh"'
)


needle_index = None

for index, line in enumerate(lines):
    if needle in line:
        needle_index = index
        break


if needle_index is None:
    raise SystemExit(0)


# Find the THEME ENGINE heading above the old block.
header_index = None

for index in range(needle_index, -1, -1):
    if lines[index].strip() == "# THEME ENGINE":
        header_index = index
        break


if header_index is None:
    raise SystemExit(
        "Could not safely locate the start "
        "of the old Zsh theme block"
    )


start = header_index


# Include the separator immediately above the heading.
if (
    start > 0
    and lines[start - 1].strip().startswith("# ===")
):
    start -= 1


# Find the final theme_load call.
end = None
startup_seen = False

for index in range(needle_index, len(lines)):
    stripped = lines[index].strip()

    if "Load current theme at startup" in stripped:
        startup_seen = True
        continue

    if startup_seen and stripped == "theme_load":
        end = index
        break


if end is None:
    raise SystemExit(
        "Could not safely locate the end "
        "of the old Zsh theme block"
    )


# Remove trailing blank lines belonging to the block.
while (
    end + 1 < len(lines)
    and not lines[end + 1].strip()
):
    end += 1


new_lines = (
    lines[:start]
    + lines[end + 1:]
)


path.write_text(
    "".join(new_lines),
    encoding="utf-8",
)
PY

  ok "Removed old inline Zsh theme block"
}

# ============================================================
# START
# ============================================================

echo
info "Arch Theme Manager migration installer"
echo

# ============================================================
# PRECHECK
# ============================================================

command -v python >/dev/null 2>&1 ||
  fail "Python is required"

python -m venv --help >/dev/null 2>&1 ||
  fail "Python venv support is required"

[[ -f "$PROJECT_DIR/pyproject.toml" ]] ||
  fail "pyproject.toml not found"

[[ -f "$PROJECT_DIR/integrations/zsh/theme.zsh" ]] ||
  fail "Zsh integration template not found"

[[ -f "$PROJECT_DIR/integrations/nvim/arch-theme-manager.lua" ]] ||
  fail "Neovim integration template not found"

# ============================================================
# CREATE DIRECTORIES
# ============================================================

mkdir -p "$ATM_CONFIG"
mkdir -p "$ATM_THEMES"
mkdir -p "$ATM_GENERATED"
mkdir -p "$ATM_INTEGRATIONS"

mkdir -p "$ATM_DATA"
mkdir -p "$ATM_STATE"

mkdir -p "$LOCAL_BIN"
mkdir -p "$BACKUP_DIR"

# ============================================================
# BACKUP CURRENT DESKTOP CONFIG
# ============================================================

info "Backing up current configuration"

backup_file "$CONFIG_HOME/hypr/hyprland.lua"
backup_file "$CONFIG_HOME/hypr/hyprlock.conf"
backup_file "$CONFIG_HOME/hypr/theme.lua"
backup_file "$CONFIG_HOME/hypr/hyprtoolkit.conf"

backup_file "$CONFIG_HOME/waybar/style.css"
backup_file "$CONFIG_HOME/waybar/theme.css"

backup_file "$CONFIG_HOME/swaync/style.css"
backup_file "$CONFIG_HOME/swaync/theme.css"

backup_file "$CONFIG_HOME/kitty/kitty.conf"
backup_file "$CONFIG_HOME/kitty/theme.conf"

backup_file "$CONFIG_HOME/nvim/plugin/arch-theme-manager.lua"

backup_file "$HOME/.zshrc"

echo

# ============================================================
# INSTALL APPLICATION VENV
# ============================================================

info "Installing Arch Theme Manager"

if [[ ! -x "$ATM_VENV/bin/python" ]]; then
  python -m venv "$ATM_VENV"

  ok "Created application virtual environment"
fi

"$ATM_VENV/bin/python" \
  -m pip install \
  --disable-pip-version-check \
  --upgrade \
  "$PROJECT_DIR"

if [[ ! -x "$ATM_VENV/bin/themectl" ]]; then
  fail "Package installed but themectl was not created"
fi

ln -sfn \
  "$ATM_VENV/bin/themectl" \
  "$ATM_BIN"

ok "Installed themectl -> $ATM_BIN"

# ============================================================
# SHELL PATH
# ============================================================

append_once \
  "$HOME/.zshrc" \
  'export PATH="$HOME/.local/bin:$PATH"'

# ============================================================
# MIGRATE / INSTALL THEMES
# ============================================================

if [[ -z "$(find "$ATM_THEMES" -mindepth 1 -maxdepth 1 -print -quit 2>/dev/null)" ]]; then

  if [[ -d "$OLD_ENGINE/themes" ]]; then
    info "Migrating themes from old theme engine"

    cp -a \
      "$OLD_ENGINE/themes/." \
      "$ATM_THEMES/"

    ok "Themes migrated"

  elif [[ -f "$PROJECT_DIR/themes/example/theme.json" ]]; then
    info "Installing bundled example theme"

    cp -a \
      "$PROJECT_DIR/themes/example" \
      "$ATM_THEMES/example"

    ok "Example theme installed"
  fi
fi

if [[ -z "$(find "$ATM_THEMES" -mindepth 1 -maxdepth 1 -print -quit 2>/dev/null)" ]]; then
  fail "No themes found in $ATM_THEMES"
fi

# ============================================================
# DETERMINE CURRENT THEME
# ============================================================

CURRENT_THEME="$(
  "$ATM_BIN" current 2>/dev/null || true
)"

if [[ "$CURRENT_THEME" == "No theme is currently active." ]]; then
  CURRENT_THEME=""
fi

# If the new manager has no state yet, migrate the old state.
if [[ -z "$CURRENT_THEME" ]] &&
  [[ -f "$OLD_ENGINE/state/current.json" ]]; then
  CURRENT_THEME="$(
    python - "$OLD_ENGINE/state/current.json" <<'PY'
from pathlib import Path
import json
import sys


path = Path(sys.argv[1])

try:
    data = json.loads(
        path.read_text(
            encoding="utf-8",
        )
    )

    current = data.get("current")

    if isinstance(current, str):
        print(current)

except Exception:
    pass
PY
  )"
fi

# Final fallback: first installed theme.
if [[ -z "$CURRENT_THEME" ]]; then
  CURRENT_THEME="$(
    "$ATM_BIN" list |
      sed 's/^[* ]*//' |
      head -n 1
  )"
fi

if [[ -z "$CURRENT_THEME" ]]; then
  fail "Could not determine an initial theme"
fi

if ! "$ATM_BIN" validate "$CURRENT_THEME" >/dev/null; then
  fail "Theme '$CURRENT_THEME' is invalid"
fi

ok "Current migration theme: $CURRENT_THEME"

# ============================================================
# FIRST GENERATION
# ============================================================

info "Generating packaged theme files"

"$ATM_BIN" apply "$CURRENT_THEME"

ok "Generated packaged theme files"

# ============================================================
# HYPRLAND MIGRATION
# ============================================================

HYPRLAND_CONFIG="$CONFIG_HOME/hypr/hyprland.lua"

ensure_file "$HYPRLAND_CONFIG"

# Replace old direct themectl path with the stable CLI path.
sed -i \
  's#\$HOME/.config/hypr/theme-engine/bin/themectl#\$HOME/.local/bin/themectl#g' \
  "$HYPRLAND_CONFIG"

append_once \
  "$HYPRLAND_CONFIG" \
  'require("theme")'

# ============================================================
# HYPRLOCK MIGRATION
# ============================================================

HYPRLOCK_CONFIG="$CONFIG_HOME/hypr/hyprlock.conf"

ensure_file "$HYPRLOCK_CONFIG"

sed -i \
  's#\$HOME/.config/hypr/theme-engine/generated/hyprlock-theme.conf#\$HOME/.config/arch-theme-manager/generated/hyprlock-theme.conf#g' \
  "$HYPRLOCK_CONFIG"

prepend_once \
  "$HYPRLOCK_CONFIG" \
  'source = $HOME/.config/arch-theme-manager/generated/hyprlock-theme.conf'

# ============================================================
# WAYBAR
# ============================================================

ensure_css_theme_import \
  "$CONFIG_HOME/waybar/style.css"

# ============================================================
# SWAYNC
# ============================================================

ensure_css_theme_import \
  "$CONFIG_HOME/swaync/style.css"

# ============================================================
# KITTY
# ============================================================

KITTY_CONFIG="$CONFIG_HOME/kitty/kitty.conf"

append_once \
  "$KITTY_CONFIG" \
  'include theme.conf'

append_once \
  "$KITTY_CONFIG" \
  'allow_remote_control socket-only'

append_once \
  "$KITTY_CONFIG" \
  'listen_on unix:/tmp/kitty-theme-{kitty_pid}'

# ============================================================
# ZSH
# ============================================================

remove_old_zsh_theme_block

cp \
  "$PROJECT_DIR/integrations/zsh/theme.zsh" \
  "$ATM_INTEGRATIONS/zsh.zsh"

append_once \
  "$HOME/.zshrc" \
  'source "${XDG_CONFIG_HOME:-$HOME/.config}/arch-theme-manager/integrations/zsh.zsh"'

ok "Installed Zsh integration"

# ============================================================
# NEOVIM
# ============================================================

info "Installing Neovim integration"

cp \
  "$PROJECT_DIR/integrations/nvim/arch-theme-manager.lua" \
  "$ATM_INTEGRATIONS/nvim.lua"

link_generated \
  "$ATM_INTEGRATIONS/nvim.lua" \
  "$CONFIG_HOME/nvim/plugin/arch-theme-manager.lua"

ok "Installed Neovim integration"

# ============================================================
# SWITCH GENERATED FILE LINKS
# ============================================================

info "Switching desktop integration links"

link_generated \
  "$ATM_GENERATED/hyprland-theme.lua" \
  "$CONFIG_HOME/hypr/theme.lua"

link_generated \
  "$ATM_GENERATED/hyprtoolkit-theme.conf" \
  "$CONFIG_HOME/hypr/hyprtoolkit.conf"

link_generated \
  "$ATM_GENERATED/waybar-theme.css" \
  "$CONFIG_HOME/waybar/theme.css"

link_generated \
  "$ATM_GENERATED/swaync-theme.css" \
  "$CONFIG_HOME/swaync/theme.css"

link_generated \
  "$ATM_GENERATED/kitty-theme.conf" \
  "$CONFIG_HOME/kitty/theme.conf"

# ============================================================
# FINAL APPLY
# ============================================================

info "Applying $CURRENT_THEME through packaged manager"

"$ATM_BIN" apply "$CURRENT_THEME"

ok "Theme applied"

# ============================================================
# DOCTOR
# ============================================================

echo
info "Running themectl doctor"
echo

if "$ATM_BIN" doctor; then
  echo
  ok "Migration completed successfully"
else
  echo
  warn "Migration completed but doctor reported problems"
fi

# ============================================================
# RESULT
# ============================================================

echo
printf 'CLI:      %s\n' "$ATM_BIN"
printf 'Package:  %s\n' "$ATM_DATA"
printf 'Config:   %s\n' "$ATM_CONFIG"
printf 'State:    %s\n' "$ATM_STATE"
printf 'Backups:  %s\n' "$BACKUP_DIR"

echo
info "Reload Zsh:"
printf '  source ~/.zshrc\n'

echo
info "Then verify:"
printf '  which themectl\n'
printf '  themectl current\n'
printf '  themectl doctor\n'

echo
warn "Do not delete $OLD_ENGINE until migration is fully verified."
