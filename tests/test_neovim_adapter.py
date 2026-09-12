from pathlib import Path

from arch_theme_manager.adapters.neovim import (
    NeovimAdapter,
)


def make_theme():
    return {
        "_theme_name": "portal",
        "colors": {
            "background": "#263C4C",
            "surface": "#3E5466",
            "foreground": "#F3E4D5",
            "primary": "#5F96AF",
            "secondary": "#DE9977",
            "accent": "#B06574",
        },
    }


def test_generates_neovim_theme(
    tmp_path,
    monkeypatch,
):
    runtime = tmp_path / "runtime"

    monkeypatch.setattr(
        "arch_theme_manager.adapters.neovim.runtime_home",
        lambda: runtime,
    )

    generated = tmp_path / "generated"

    adapter = NeovimAdapter(
        generated,
    )

    adapter.apply(make_theme())

    target = generated / "nvim-theme.lua"

    assert target.is_file()


def test_generated_theme_contains_palette(
    tmp_path,
    monkeypatch,
):
    runtime = tmp_path / "runtime"

    monkeypatch.setattr(
        "arch_theme_manager.adapters.neovim.runtime_home",
        lambda: runtime,
    )

    generated = tmp_path / "generated"

    adapter = NeovimAdapter(
        generated,
    )

    adapter.apply(make_theme())

    content = (generated / "nvim-theme.lua").read_text(
        encoding="utf-8",
    )

    assert "#263C4C" in content

    assert "#3E5466" in content

    assert "#F3E4D5" in content

    assert "#5F96AF" in content

    assert "#DE9977" in content

    assert "#B06574" in content


def test_generated_theme_contains_name(
    tmp_path,
    monkeypatch,
):
    runtime = tmp_path / "runtime"

    monkeypatch.setattr(
        "arch_theme_manager.adapters.neovim.runtime_home",
        lambda: runtime,
    )

    generated = tmp_path / "generated"

    adapter = NeovimAdapter(
        generated,
    )

    adapter.apply(make_theme())

    content = (generated / "nvim-theme.lua").read_text(
        encoding="utf-8",
    )

    assert 'name = "portal"' in content


def test_generated_theme_sets_colorscheme_name(
    tmp_path,
    monkeypatch,
):
    runtime = tmp_path / "runtime"

    monkeypatch.setattr(
        "arch_theme_manager.adapters.neovim.runtime_home",
        lambda: runtime,
    )

    generated = tmp_path / "generated"

    adapter = NeovimAdapter(
        generated,
    )

    adapter.apply(make_theme())

    content = (generated / "nvim-theme.lua").read_text(
        encoding="utf-8",
    )

    assert 'vim.g.colors_name = "arch-theme-manager"' in content


def test_atomic_generation_leaves_no_temp_file(
    tmp_path,
    monkeypatch,
):
    runtime = tmp_path / "runtime"

    monkeypatch.setattr(
        "arch_theme_manager.adapters.neovim.runtime_home",
        lambda: runtime,
    )

    generated = tmp_path / "generated"

    adapter = NeovimAdapter(
        generated,
    )

    adapter.apply(make_theme())

    assert not (generated / "nvim-theme.tmp").exists()


def test_no_runtime_directory_is_safe(
    tmp_path,
    monkeypatch,
):
    runtime = tmp_path / "missing-runtime"

    monkeypatch.setattr(
        "arch_theme_manager.adapters.neovim.runtime_home",
        lambda: runtime,
    )

    adapter = NeovimAdapter(
        tmp_path / "generated",
    )

    adapter.apply(make_theme())


def test_reloads_registered_neovim_instance(
    tmp_path,
    monkeypatch,
):
    runtime = tmp_path / "runtime"

    socket_dir = runtime / "nvim"

    socket_dir.mkdir(
        parents=True,
    )

    socket = socket_dir / "1234.sock"

    socket.touch()

    monkeypatch.setattr(
        "arch_theme_manager.adapters.neovim.runtime_home",
        lambda: runtime,
    )

    calls = []

    class Result:
        returncode = 0
        stdout = ""
        stderr = ""

    def fake_run(
        command,
        **kwargs,
    ):
        calls.append(command)

        return Result()

    monkeypatch.setattr(
        "arch_theme_manager.adapters.neovim.subprocess.run",
        fake_run,
    )

    adapter = NeovimAdapter(
        tmp_path / "generated",
    )

    adapter.apply(make_theme())

    assert len(calls) == 1

    assert calls[0] == [
        "nvim",
        "--server",
        str(socket),
        "--remote-expr",
        'execute("ArchThemeReload")',
    ]


def test_failed_reload_removes_stale_socket(
    tmp_path,
    monkeypatch,
):
    runtime = tmp_path / "runtime"

    socket_dir = runtime / "nvim"

    socket_dir.mkdir(
        parents=True,
    )

    socket = socket_dir / "1234.sock"

    socket.touch()

    monkeypatch.setattr(
        "arch_theme_manager.adapters.neovim.runtime_home",
        lambda: runtime,
    )

    class Result:
        returncode = 1
        stdout = ""
        stderr = "connection failed"

    monkeypatch.setattr(
        "arch_theme_manager.adapters.neovim.subprocess.run",
        lambda *args, **kwargs: Result(),
    )

    adapter = NeovimAdapter(
        tmp_path / "generated",
    )

    adapter.apply(make_theme())

    assert not socket.exists()
