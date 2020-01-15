import pytest


@pytest.fixture(autouse=True)
def unset_env(monkeypatch):
    monkeypatch.delenv("ANYMOTION_ROOT", raising=False)
    monkeypatch.delenv("ANYMOTION_CLIENT_ID", raising=False)
    monkeypatch.delenv("ANYMOTION_CLIENT_SECRET", raising=False)
    monkeypatch.setenv("STDOUT_ISSHOW", "True")
