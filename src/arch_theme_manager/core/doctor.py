from pathlib import Path
import os
import shutil
import subprocess


class ThemeDoctor:
    def __init__(
        self,
        loader,
        validator,
        state,
        generated_dir: Path,
    ):
        self.loader = loader
        self.validator = validator
        self.state = state
        self.generated_dir = generated_dir

        self.home = Path.home()

        self.config_root = Path(
            os.environ.get(
                "XDG_CONFIG_HOME",
                self.home / ".config",
            )
        )

        self.manager_config = self.config_root / "arch-theme-manager"

        runtime_dir = os.environ.get("XDG_RUNTIME_DIR")

        if runtime_dir:
            self.runtime_root = Path(runtime_dir) / "arch-theme-manager"
        else:
            self.runtime_root = Path("/tmp") / (f"arch-theme-manager-{os.getuid()}")

    # ========================================================
    # RUN
    # ========================================================

    def run(self) -> bool:
        checks = []

        checks.extend(self._check_themes())

        checks.extend(self._check_current_theme())

        checks.extend(self._check_commands())

        checks.extend(self._check_processes())

        checks.extend(self._check_generated_files())

        checks.extend(self._check_integrations())

        checks.extend(self._check_neovim_runtime())

        checks.extend(self._check_hyprland())

        print("Arch Theme Manager Doctor")

        print()

        failures = 0
        warnings = 0

        for status, message in checks:
            print(f"[{status}] {message}")

            if status == "FAIL":
                failures += 1

            elif status == "WARN":
                warnings += 1

        print()

        if failures:
            print(f"Doctor found {failures} failure(s) and {warnings} warning(s).")

            return False

        if warnings:
            print(f"System is functional with {warnings} warning(s).")

            return True

        print("Everything looks healthy.")

        return True

    # ========================================================
    # THEMES
    # ========================================================

    def _check_themes(self):
        results = []

        try:
            themes = self.loader.list_themes()

        except Exception as exc:
            return [
                (
                    "FAIL",
                    f"Could not list themes: {exc}",
                )
            ]

        if not themes:
            return [
                (
                    "FAIL",
                    "No themes are installed.",
                )
            ]

        valid = 0

        for theme_name in themes:
            try:
                theme = self.loader.load(theme_name)

                self.validator.validate(theme)

                valid += 1

            except Exception as exc:
                results.append(
                    (
                        "FAIL",
                        f"Theme '{theme_name}' is invalid: {exc}",
                    )
                )

        results.insert(
            0,
            (
                "OK",
                f"{valid}/{len(themes)} themes validated",
            ),
        )

        return results

    # ========================================================
    # CURRENT THEME
    # ========================================================

    def _check_current_theme(self):
        current = self.state.current()

        if current is None:
            return [
                (
                    "WARN",
                    "No current theme is recorded.",
                )
            ]

        try:
            themes = self.loader.list_themes()

        except Exception as exc:
            return [
                (
                    "FAIL",
                    f"Could not check current theme: {exc}",
                )
            ]

        if current not in themes:
            return [
                (
                    "FAIL",
                    f"Current theme '{current}' does not exist.",
                )
            ]

        return [
            (
                "OK",
                f"Current theme: {current}",
            )
        ]

    # ========================================================
    # REQUIRED COMMANDS
    # ========================================================

    def _check_commands(self):
        required = [
            "hyprctl",
            "hyprpaper",
            "waybar",
            "swaync-client",
            "kitty",
            "zsh",
            "hyprlock",
            "hyprlauncher",
        ]

        results = []

        for command in required:
            path = shutil.which(command)

            if path:
                results.append(
                    (
                        "OK",
                        f"{command}: {path}",
                    )
                )

            else:
                results.append(
                    (
                        "FAIL",
                        f"Required command '{command}' not found",
                    )
                )

        kitten = shutil.which("kitten")

        if kitten:
            results.append(
                (
                    "OK",
                    f"kitten: {kitten}",
                )
            )

        else:
            results.append(
                (
                    "WARN",
                    "kitten command not found",
                )
            )

        nvim = shutil.which("nvim")

        if nvim:
            results.append(
                (
                    "OK",
                    f"nvim: {nvim}",
                )
            )

        else:
            results.append(
                (
                    "WARN",
                    "nvim command not found; Neovim integration cannot be used",
                )
            )

        return results

    # ========================================================
    # RUNNING PROCESSES
    # ========================================================

    def _check_processes(self):
        results = []

        required = [
            "hyprpaper",
            "waybar",
            "swaync",
            "hyprlauncher",
        ]

        for process in required:
            if self._process_running(process):
                results.append(
                    (
                        "OK",
                        f"{process} is running",
                    )
                )

            else:
                results.append(
                    (
                        "FAIL",
                        f"{process} is not running",
                    )
                )

        optional = [
            "kitty",
            "hyprlock",
        ]

        for process in optional:
            if self._process_running(process):
                results.append(
                    (
                        "OK",
                        f"{process} is running",
                    )
                )

            else:
                results.append(
                    (
                        "WARN",
                        f"{process} is not currently running",
                    )
                )

        return results

    # ========================================================
    # GENERATED FILES
    # ========================================================

    def _check_generated_files(self):
        expected = [
            "waybar-theme.css",
            "swaync-theme.css",
            "hyprland-theme.lua",
            "kitty-theme.conf",
            "zsh-theme.zsh",
            "nvim-theme.lua",
            "hyprlock-theme.conf",
            "hyprtoolkit-theme.conf",
        ]

        results = []

        for filename in expected:
            path = self.generated_dir / filename

            if not path.is_file():
                results.append(
                    (
                        "FAIL",
                        f"Missing generated file: {filename}",
                    )
                )

                continue

            try:
                size = path.stat().st_size

            except OSError as exc:
                results.append(
                    (
                        "FAIL",
                        f"Could not inspect {filename}: {exc}",
                    )
                )

                continue

            if size == 0:
                results.append(
                    (
                        "FAIL",
                        f"Generated file is empty: {filename}",
                    )
                )

                continue

            results.append(
                (
                    "OK",
                    f"Generated: {filename}",
                )
            )

        return results

    # ========================================================
    # INTEGRATIONS
    # ========================================================

    def _check_integrations(self):
        results = []

        hypr_dir = self.config_root / "hypr"

        waybar_dir = self.config_root / "waybar"

        swaync_dir = self.config_root / "swaync"

        kitty_dir = self.config_root / "kitty"

        nvim_dir = self.config_root / "nvim"

        integrations = [
            (
                waybar_dir / "theme.css",
                self.generated_dir / "waybar-theme.css",
                "Waybar",
            ),
            (
                swaync_dir / "theme.css",
                self.generated_dir / "swaync-theme.css",
                "SwayNC",
            ),
            (
                hypr_dir / "theme.lua",
                self.generated_dir / "hyprland-theme.lua",
                "Hyprland",
            ),
            (
                kitty_dir / "theme.conf",
                self.generated_dir / "kitty-theme.conf",
                "Kitty",
            ),
            (
                hypr_dir / "hyprtoolkit.conf",
                self.generated_dir / "hyprtoolkit-theme.conf",
                "Hyprtoolkit",
            ),
        ]

        for link, target, name in integrations:
            results.append(
                self._check_symlink(
                    link,
                    target,
                    name,
                )
            )

        # ----------------------------------------------------
        # HYPRLAND
        # ----------------------------------------------------

        hyprland_config = hypr_dir / "hyprland.lua"

        results.append(
            self._file_contains(
                hyprland_config,
                'require("theme")',
                "Hyprland theme require",
            )
        )

        # ----------------------------------------------------
        # HYPRLOCK
        # ----------------------------------------------------

        hyprlock_config = hypr_dir / "hyprlock.conf"

        results.append(
            self._file_contains(
                hyprlock_config,
                ("arch-theme-manager/generated/hyprlock-theme.conf"),
                "Hyprlock theme source",
            )
        )

        # ----------------------------------------------------
        # KITTY
        # ----------------------------------------------------

        kitty_config = kitty_dir / "kitty.conf"

        results.append(
            self._file_contains(
                kitty_config,
                "include theme.conf",
                "Kitty theme include",
            )
        )

        results.append(
            self._file_contains(
                kitty_config,
                ("allow_remote_control socket-only"),
                "Kitty remote control",
            )
        )

        results.append(
            self._file_contains(
                kitty_config,
                ("listen_on unix:/tmp/kitty-theme-{kitty_pid}"),
                "Kitty theme socket",
            )
        )

        # ----------------------------------------------------
        # SWAYNC
        # ----------------------------------------------------

        swaync_style = swaync_dir / "style.css"

        results.append(
            self._file_contains(
                swaync_style,
                "theme.css",
                "SwayNC theme import",
            )
        )

        # ----------------------------------------------------
        # WAYBAR
        # ----------------------------------------------------

        waybar_style = waybar_dir / "style.css"

        results.append(
            self._file_contains(
                waybar_style,
                "theme.css",
                "Waybar theme import",
            )
        )

        # ----------------------------------------------------
        # ZSH
        # ----------------------------------------------------

        zshrc = self.home / ".zshrc"

        results.append(
            self._file_contains(
                zshrc,
                ("arch-theme-manager/integrations/zsh.zsh"),
                "Zsh theme integration",
            )
        )

        zsh_integration = self.manager_config / "integrations" / "zsh.zsh"

        if zsh_integration.is_file():
            results.append(
                (
                    "OK",
                    "Zsh integration file",
                )
            )

        else:
            results.append(
                (
                    "FAIL",
                    "Zsh integration file missing",
                )
            )

        # ----------------------------------------------------
        # NEOVIM
        # ----------------------------------------------------

        nvim_integration = self.manager_config / "integrations" / "nvim.lua"

        if nvim_integration.is_file():
            results.append(
                (
                    "OK",
                    "Neovim integration file",
                )
            )

        else:
            results.append(
                (
                    "FAIL",
                    "Neovim integration file missing",
                )
            )

        nvim_plugin = nvim_dir / "plugin" / "arch-theme-manager.lua"

        results.append(
            self._check_symlink(
                nvim_plugin,
                nvim_integration,
                "Neovim",
            )
        )

        return results

    # ========================================================
    # NEOVIM RPC
    # ========================================================

    def _check_neovim_runtime(self):
        results = []

        nvim_path = shutil.which(
            "nvim"
        )

        if not nvim_path:
            return [
                (
                    "WARN",
                    "Neovim RPC check skipped "
                    "because nvim is not installed",
                )
            ]

        running = self._process_running(
            "nvim"
        )

        socket_dir = (
            self.runtime_root
            / "nvim"
        )

        if not running:
            results.append(
                (
                    "WARN",
                    "Neovim is not currently "
                    "running",
                )
            )

            if socket_dir.is_dir():
                sockets = list(
                    socket_dir.glob(
                        "*.sock"
                    )
                )

                if sockets:
                    results.append(
                        (
                            "WARN",
                            f"{len(sockets)} stale "
                            f"Neovim RPC socket(s) "
                            f"may remain",
                        )
                    )

            return results

        if not socket_dir.is_dir():
            return [
                (
                    "FAIL",
                    "Neovim is running but "
                    "Arch Theme Manager RPC "
                    "directory is missing",
                )
            ]

        sockets = []

        for path in socket_dir.glob(
            "*.sock"
        ):
            try:
                if path.is_socket():
                    sockets.append(
                        path
                    )

            except OSError:
                continue

        if not sockets:
            return [
                (
                    "FAIL",
                    "Neovim is running but "
                    "no Arch Theme Manager "
                    "RPC socket is registered",
                )
            ]

        responsive = 0
        unresponsive = 0

        for socket in sockets:
            try:
                result = subprocess.run(
                    [
                        nvim_path,
                        "--server",
                        str(socket),
                        "--remote-expr",
                        'execute("ArchThemeReload")',
                    ],
                    capture_output=True,
                    text=True,
                    timeout=3,
                )

            except (
                OSError,
                subprocess.TimeoutExpired,
            ):
                unresponsive += 1
                continue

            if result.returncode == 0:
                responsive += 1

            else:
                unresponsive += 1

        if responsive:
            results.append(
                (
                    "OK",
                    f"{responsive} Neovim RPC "
                    f"instance(s) registered",
                )
            )

        else:
            results.append(
                (
                    "FAIL",
                    "No responsive Arch Theme "
                    "Manager Neovim RPC "
                    "instances were found",
                )
            )

        if unresponsive:
            results.append(
                (
                    "WARN",
                    f"{unresponsive} "
                    f"unresponsive Neovim RPC "
                    f"socket(s) found",
                )
            )

        return results

    # ========================================================
    # HYPRLAND
    # ========================================================

    def _check_hyprland(self):
        results = []

        try:
            result = subprocess.run(
                [
                    "hyprctl",
                    "version",
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )

        except Exception as exc:
            return [
                (
                    "FAIL",
                    f"Could not communicate with Hyprland: {exc}",
                )
            ]

        if result.returncode != 0:
            return [
                (
                    "FAIL",
                    "Could not communicate with Hyprland",
                )
            ]

        results.append(
            (
                "OK",
                "Hyprland IPC reachable",
            )
        )

        try:
            result = subprocess.run(
                [
                    "hyprctl",
                    "configerrors",
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )

            output = result.stdout.strip()

            if result.returncode != 0:
                results.append(
                    (
                        "FAIL",
                        "Could not check Hyprland config errors",
                    )
                )

            elif output:
                results.append(
                    (
                        "FAIL",
                        f"Hyprland config errors: {output}",
                    )
                )

            else:
                results.append(
                    (
                        "OK",
                        "Hyprland configuration has no errors",
                    )
                )

        except Exception as exc:
            results.append(
                (
                    "WARN",
                    f"Could not inspect Hyprland config errors: {exc}",
                )
            )

        return results

    # ========================================================
    # HELPERS
    # ========================================================

    @staticmethod
    def _process_running(
        process: str,
    ) -> bool:
        try:
            result = subprocess.run(
                [
                    "pgrep",
                    "-u",
                    str(os.getuid()),
                    "-x",
                    process,
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=5,
            )

        except (
            OSError,
            subprocess.TimeoutExpired,
        ):
            return False

        return result.returncode == 0

    @staticmethod
    def _check_symlink(
        link: Path,
        target: Path,
        name: str,
    ):
        if not link.exists() and not link.is_symlink():
            return (
                "FAIL",
                f"{name} integration is missing: {link}",
            )

        if not link.is_symlink():
            return (
                "WARN",
                f"{name} integration exists but is not a symlink",
            )

        try:
            actual = link.resolve()
            expected = target.resolve()

        except OSError as exc:
            return (
                "FAIL",
                f"{name} integration cannot be resolved: {exc}",
            )

        if actual != expected:
            return (
                "FAIL",
                f"{name} points to wrong target: {actual}",
            )

        return (
            "OK",
            f"{name} integration",
        )

    @staticmethod
    def _file_contains(
        path: Path,
        text: str,
        description: str,
    ):
        if not path.is_file():
            return (
                "FAIL",
                f"{description}: file missing ({path})",
            )

        try:
            content = path.read_text(
                encoding="utf-8",
            )

        except OSError as exc:
            return (
                "FAIL",
                f"{description}: {exc}",
            )

        if text not in content:
            return (
                "FAIL",
                f"{description}: not configured",
            )

        return (
            "OK",
            description,
        )
