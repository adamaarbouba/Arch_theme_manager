# Example Theme

This is a minimal working Arch Theme Manager theme.

## Structure

```text
example/
├── theme.json
└── wallpaper.png
```

Copy it into your theme directory:

```bash
cp -r themes/example \
    ~/.config/arch-theme-manager/themes/my-theme
```

Then edit:

```text
~/.config/arch-theme-manager/themes/my-theme/theme.json
```

Validate:

```bash
themectl validate my-theme
```

Apply:

```bash
themectl apply my-theme
```
