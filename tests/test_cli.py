from pathlib import Path
import subprocess
import sys


def test_themectl_help():
    executable = (
        Path(sys.executable).parent
        / "themectl"
    )

    assert executable.is_file()

    result = subprocess.run(
        [
            str(executable),
            "--help",
        ],
        capture_output=True,
        text=True,
        timeout=5,
    )

    assert result.returncode == 0

    assert (
        "Arch Linux / Hyprland "
        "theme orchestrator"
        in result.stdout
    )

    assert "apply" in result.stdout
    assert "doctor" in result.stdout
    assert "next" in result.stdout
    assert "previous" in result.stdout
