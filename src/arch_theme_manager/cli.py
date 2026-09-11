#!/usr/bin/env python3

import argparse
import json
import sys
from pathlib import Path

from .core.doctor import ThemeDoctor
from .core.loader import ThemeError, ThemeLoader
from .core.orchestrator import (
    ThemeApplyError,
    ThemeOrchestrator,
)
from .core.state import ThemeState
from .core.theme_installer import (
    ThemeInstallError,
    ThemeInstaller,
)
from .core.validator import (
    ThemeValidationError,
    ThemeValidator,
)
from .paths import (
    ensure_runtime_dirs,
    generated_dir,
    state_dir,
    themes_dir,
)


loader = None
validator = None
state = None
orchestrator = None
doctor = None
installer = None


# ============================================================
# INITIALIZATION
# ============================================================

def initialize() -> None:
    global loader
    global validator
    global state
    global orchestrator
    global doctor
    global installer

    ensure_runtime_dirs()

    loader = ThemeLoader(
        themes_dir(),
    )

    validator = ThemeValidator()

    state = ThemeState(
        state_dir(),
    )

    orchestrator = ThemeOrchestrator(
        loader=loader,
        validator=validator,
        state=state,
        generated_dir=generated_dir(),
    )

    doctor = ThemeDoctor(
        loader=loader,
        validator=validator,
        state=state,
        generated_dir=generated_dir(),
    )

    installer = ThemeInstaller(
        themes_dir(),
        validator,
    )


# ============================================================
# LIST
# ============================================================

def command_list(_args):
    themes = loader.list_themes()

    if not themes:
        print("No themes found.")
        return

    current = state.current()

    for theme in themes:
        marker = (
            "*"
            if theme == current
            else " "
        )

        print(
            f"{marker} {theme}"
        )


# ============================================================
# SHOW
# ============================================================

def command_show(args):
    theme = loader.load(
        args.theme,
    )

    public_data = {
        key: value
        for key, value in theme.items()
        if not key.startswith("_")
    }

    print(
        json.dumps(
            public_data,
            indent=4,
        )
    )


# ============================================================
# VALIDATE
# ============================================================

def command_validate(args):
    theme = loader.load(
        args.theme,
    )

    validator.validate(
        theme,
    )

    print(
        f"Theme '{args.theme}' is valid."
    )


# ============================================================
# APPLY
# ============================================================

def command_apply(args):
    orchestrator.apply(
        args.theme,
    )

    print(
        f"Applied theme '{args.theme}'."
    )


# ============================================================
# CURRENT
# ============================================================

def command_current(_args):
    current = state.current()

    if current is None:
        print(
            "No theme is currently active."
        )
        return

    print(current)


# ============================================================
# NEXT
# ============================================================

def command_next(_args):
    themes = loader.list_themes()

    if not themes:
        print("No themes found.")
        return

    current = state.current()

    if current not in themes:
        target = themes[0]

    else:
        index = themes.index(
            current,
        )

        target = themes[
            (index + 1)
            % len(themes)
        ]

    orchestrator.apply(
        target,
    )

    print(
        f"Applied theme '{target}'."
    )


# ============================================================
# PREVIOUS
# ============================================================

def command_previous(_args):
    themes = loader.list_themes()

    if not themes:
        print("No themes found.")
        return

    current = state.current()

    if current not in themes:
        target = themes[-1]

    else:
        index = themes.index(
            current,
        )

        target = themes[
            (index - 1)
            % len(themes)
        ]

    orchestrator.apply(
        target,
    )

    print(
        f"Applied theme '{target}'."
    )


# ============================================================
# INSTALL THEME
# ============================================================

def command_install_theme(args):
    theme_name = installer.install(
        Path(args.path),
        name=args.name,
        force=args.force,
    )

    print(
        f"Installed theme '{theme_name}'."
    )


# ============================================================
# DOCTOR
# ============================================================

def command_doctor(_args):
    healthy = doctor.run()

    if not healthy:
        sys.exit(1)


# ============================================================
# PARSER
# ============================================================

def build_parser():
    parser = argparse.ArgumentParser(
        prog="themectl",
        description=(
            "Arch Linux / Hyprland "
            "theme orchestrator"
        ),
    )

    subcommands = parser.add_subparsers(
        dest="command",
        required=True,
    )

    # --------------------------------------------------------
    # LIST
    # --------------------------------------------------------

    list_parser = subcommands.add_parser(
        "list",
        help="List installed themes",
    )

    list_parser.set_defaults(
        function=command_list,
    )

    # --------------------------------------------------------
    # SHOW
    # --------------------------------------------------------

    show_parser = subcommands.add_parser(
        "show",
        help=(
            "Show resolved theme "
            "configuration"
        ),
    )

    show_parser.add_argument(
        "theme",
    )

    show_parser.set_defaults(
        function=command_show,
    )

    # --------------------------------------------------------
    # VALIDATE
    # --------------------------------------------------------

    validate_parser = (
        subcommands.add_parser(
            "validate",
            help="Validate a theme",
        )
    )

    validate_parser.add_argument(
        "theme",
    )

    validate_parser.set_defaults(
        function=command_validate,
    )

    # --------------------------------------------------------
    # APPLY
    # --------------------------------------------------------

    apply_parser = subcommands.add_parser(
        "apply",
        help="Apply a theme",
    )

    apply_parser.add_argument(
        "theme",
    )

    apply_parser.set_defaults(
        function=command_apply,
    )

    # --------------------------------------------------------
    # CURRENT
    # --------------------------------------------------------

    current_parser = (
        subcommands.add_parser(
            "current",
            help="Show current theme",
        )
    )

    current_parser.set_defaults(
        function=command_current,
    )

    # --------------------------------------------------------
    # NEXT
    # --------------------------------------------------------

    next_parser = subcommands.add_parser(
        "next",
        help="Apply the next theme",
    )

    next_parser.set_defaults(
        function=command_next,
    )

    # --------------------------------------------------------
    # PREVIOUS
    # --------------------------------------------------------

    previous_parser = (
        subcommands.add_parser(
            "previous",
            help="Apply the previous theme",
        )
    )

    previous_parser.set_defaults(
        function=command_previous,
    )

    # --------------------------------------------------------
    # INSTALL THEME
    # --------------------------------------------------------

    install_parser = (
        subcommands.add_parser(
            "install-theme",
            help=(
                "Install a theme "
                "from a directory"
            ),
            description=(
                "Install a theme "
                "from a directory"
            ),
        )
    )

    install_parser.add_argument(
        "path",
        help=(
            "Path to the theme "
            "directory"
        ),
    )

    install_parser.add_argument(
        "--name",
        help=(
            "Install using a "
            "different theme name"
        ),
    )

    install_parser.add_argument(
        "--force",
        action="store_true",
        help=(
            "Replace an existing "
            "theme"
        ),
    )

    install_parser.set_defaults(
        function=command_install_theme,
    )

    # --------------------------------------------------------
    # DOCTOR
    # --------------------------------------------------------

    doctor_parser = (
        subcommands.add_parser(
            "doctor",
            help=(
                "Check theme manager "
                "health"
            ),
        )
    )

    doctor_parser.set_defaults(
        function=command_doctor,
    )

    return parser


# ============================================================
# MAIN
# ============================================================

def main():
    parser = build_parser()

    args = parser.parse_args()

    initialize()

    try:
        args.function(
            args,
        )

    except (
        ThemeError,
        ThemeValidationError,
        ThemeApplyError,
        ThemeInstallError,
    ) as exc:
        print(
            f"Error: {exc}",
            file=sys.stderr,
        )

        sys.exit(1)


if __name__ == "__main__":
    main()
