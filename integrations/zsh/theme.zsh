# Arch Theme Manager - Zsh integration

ATM_CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}/arch-theme-manager"

if [[ -n "${XDG_RUNTIME_DIR:-}" ]]; then
    ATM_RUNTIME_HOME="$XDG_RUNTIME_DIR/arch-theme-manager"
else
    ATM_RUNTIME_HOME="/tmp/arch-theme-manager-$UID"
fi

ATM_THEME_FILE="$ATM_CONFIG_HOME/generated/zsh-theme.zsh"
ATM_ZSH_RUNTIME="$ATM_RUNTIME_HOME/zsh"
ATM_ZSH_PID_FILE="$ATM_ZSH_RUNTIME/$$"


# ============================================================
# REGISTER SHELL
# ============================================================

mkdir -p "$ATM_ZSH_RUNTIME"
touch "$ATM_ZSH_PID_FILE"


# ============================================================
# LOAD THEME
# ============================================================

atm_theme_load() {
    if [[ -r "$ATM_THEME_FILE" ]]; then
        source "$ATM_THEME_FILE"
    fi
}


# ============================================================
# UNREGISTER SHELL
# ============================================================

atm_theme_unregister() {
    rm -f "$ATM_ZSH_PID_FILE"
}


# ============================================================
# LIVE THEME RELOAD
# ============================================================

TRAPUSR1() {
    atm_theme_load

    zle reset-prompt 2>/dev/null || true
    zle -R 2>/dev/null || true

    return 0
}


# ============================================================
# EXIT HOOK
# ============================================================

autoload -Uz add-zsh-hook
add-zsh-hook zshexit atm_theme_unregister


# ============================================================
# INITIAL LOAD
# ============================================================

atm_theme_load
