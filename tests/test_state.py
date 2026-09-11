from arch_theme_manager.core.state import ThemeState


def test_state_starts_empty(tmp_path):
    state = ThemeState(tmp_path)

    assert state.current() is None
    assert state.previous() is None


def test_state_saves_current_theme(tmp_path):
    state = ThemeState(tmp_path)

    state.save("portal")

    assert state.current() == "portal"
    assert state.previous() is None


def test_state_tracks_previous_theme(tmp_path):
    state = ThemeState(tmp_path)

    state.save("portal")
    state.save("lucy")

    assert state.current() == "lucy"
    assert state.previous() == "portal"


def test_state_updates_previous_each_time(tmp_path):
    state = ThemeState(tmp_path)

    state.save("portal")
    state.save("lucy")
    state.save("orbital")

    assert state.current() == "orbital"
    assert state.previous() == "lucy"


def test_state_file_is_created(tmp_path):
    state = ThemeState(tmp_path)

    state.save("portal")

    assert (
        tmp_path / "current.json"
    ).is_file()

def test_state_can_be_cleared(tmp_path):
    state = ThemeState(tmp_path)

    state.save("portal")
    state.save("lucy")

    state.clear()

    assert state.current() is None
    assert state.previous() is None
