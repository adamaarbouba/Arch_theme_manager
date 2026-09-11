from pathlib import Path


class ThemeValidationError(Exception):
    pass


class ThemeValidator:
    REQUIRED_COLORS = {
        "background",
        "surface",
        "foreground",
        "primary",
        "secondary",
        "accent",
    }

    VALID_FIT_MODES = {
        "cover",
        "contain",
        "tile",
    }

    def validate(self, theme: dict) -> None:
        errors = []

        self._validate_name(theme, errors)
        self._validate_wallpaper(theme, errors)
        self._validate_colors(theme, errors)
        self._validate_hyprpaper(theme, errors)
        self._validate_window(theme, errors)

        if errors:
            formatted = "\n".join(
                f"  - {error}"
                for error in errors
            )

            raise ThemeValidationError(
                f"Theme validation failed:\n{formatted}"
            )

    # ========================================================
    # NAME
    # ========================================================

    def _validate_name(
        self,
        theme: dict,
        errors: list[str],
    ) -> None:
        name = theme.get("name")

        if not isinstance(name, str) or not name.strip():
            errors.append(
                "'name' must be a non-empty string"
            )

    # ========================================================
    # WALLPAPER
    # ========================================================

    def _validate_wallpaper(
        self,
        theme: dict,
        errors: list[str],
    ) -> None:
        wallpaper = theme.get("wallpaper")

        if not isinstance(wallpaper, str):
            errors.append(
                "'wallpaper' must be a string"
            )
            return

        if not wallpaper.strip():
            errors.append(
                "'wallpaper' must not be empty"
            )
            return

        theme_dir = Path(
            theme["_theme_dir"]
        )

        wallpaper_path = Path(
            wallpaper
        ).expanduser()

        if not wallpaper_path.is_absolute():
            wallpaper_path = (
                theme_dir
                / wallpaper_path
            )

        if not wallpaper_path.is_file():
            errors.append(
                f"Wallpaper does not exist: "
                f"{wallpaper_path}"
            )

    # ========================================================
    # COLORS
    # ========================================================

    def _validate_colors(
        self,
        theme: dict,
        errors: list[str],
    ) -> None:
        colors = theme.get("colors")

        if not isinstance(colors, dict):
            errors.append(
                "'colors' must be an object"
            )
            return

        missing = (
            self.REQUIRED_COLORS
            - colors.keys()
        )

        for color in sorted(missing):
            errors.append(
                f"Missing color: colors.{color}"
            )

        for name, value in colors.items():
            if not isinstance(value, str):
                errors.append(
                    f"colors.{name} must be a string"
                )
                continue

            if not self._valid_hex(value):
                errors.append(
                    f"colors.{name} has invalid "
                    f"hex color: {value}"
                )

    # ========================================================
    # HYPRPAPER
    # ========================================================

    def _validate_hyprpaper(
        self,
        theme: dict,
        errors: list[str],
    ) -> None:
        config = theme.get(
            "hyprpaper",
            {},
        )

        if not isinstance(config, dict):
            errors.append(
                "'hyprpaper' must be an object"
            )
            return

        fit_mode = config.get(
            "fit_mode",
            "cover",
        )

        if fit_mode not in self.VALID_FIT_MODES:
            errors.append(
                f"Invalid hyprpaper fit_mode: "
                f"{fit_mode}"
            )

        monitor = config.get(
            "monitor",
            "",
        )

        if not isinstance(monitor, str):
            errors.append(
                "hyprpaper.monitor must be a string"
            )

    # ========================================================
    # WINDOW
    # ========================================================

    def _validate_window(
        self,
        theme: dict,
        errors: list[str],
    ) -> None:
        window = theme.get(
            "window",
            {},
        )

        if not isinstance(window, dict):
            errors.append(
                "'window' must be an object"
            )
            return

        # ----------------------------------------------------
        # rounding
        # ----------------------------------------------------

        if "rounding" in window:
            rounding = window["rounding"]

            if (
                not self._is_number(rounding)
                or rounding < 0
            ):
                errors.append(
                    "window.rounding must be "
                    "a number >= 0"
                )

        # ----------------------------------------------------
        # rounding_power
        # ----------------------------------------------------

        if "rounding_power" in window:
            rounding_power = (
                window["rounding_power"]
            )

            if (
                not self._is_number(
                    rounding_power
                )
                or rounding_power <= 0
            ):
                errors.append(
                    "window.rounding_power must "
                    "be a number > 0"
                )

        # ----------------------------------------------------
        # opacity
        # ----------------------------------------------------

        if "opacity" in window:
            opacity = window["opacity"]

            if (
                not self._is_number(opacity)
                or opacity < 0
                or opacity > 1
            ):
                errors.append(
                    "window.opacity must be "
                    "between 0 and 1"
                )

        # ----------------------------------------------------
        # border_size
        # ----------------------------------------------------

        if "border_size" in window:
            border_size = (
                window["border_size"]
            )

            if (
                not isinstance(
                    border_size,
                    int,
                )
                or isinstance(
                    border_size,
                    bool,
                )
                or border_size < 0
            ):
                errors.append(
                    "window.border_size must "
                    "be an integer >= 0"
                )

    # ========================================================
    # HELPERS
    # ========================================================

    @staticmethod
    def _valid_hex(
        value: str,
    ) -> bool:
        if not value.startswith("#"):
            return False

        hexadecimal = value[1:]

        if len(hexadecimal) not in (6, 8):
            return False

        try:
            int(
                hexadecimal,
                16,
            )

            return True

        except ValueError:
            return False

    @staticmethod
    def _is_number(
        value,
    ) -> bool:
        return (
            isinstance(
                value,
                (int, float),
            )
            and not isinstance(
                value,
                bool,
            )
        )
