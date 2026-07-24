from plugins import memory


def test_user_memory_provider_loader_skips_packaging_and_test_scripts(tmp_path, monkeypatch):
    """Loading a user provider must not execute setup.py or conftest.py."""
    user_plugins = tmp_path / "plugins"
    provider_dir = user_plugins / "mnemosyne"
    provider_dir.mkdir(parents=True)

    (provider_dir / "__init__.py").write_text(
        "class Provider:\n"
        "    def is_available(self):\n"
        "        return True\n"
        "\n"
        "def register(ctx):\n"
        "    ctx.register_memory_provider(Provider())\n",
        encoding="utf-8",
    )
    (provider_dir / "provider.py").write_text("VALUE = 1\n", encoding="utf-8")
    for filename in ("setup.py", "conftest.py"):
        (provider_dir / filename).write_text(
            f"raise SystemExit('{filename} must not be imported by memory provider loading')\n",
            encoding="utf-8",
        )

    monkeypatch.setattr(memory, "_get_user_plugins_dir", lambda: user_plugins)
    for module_name in (
        "_hermes_user_memory.mnemosyne",
        "_hermes_user_memory.mnemosyne.provider",
        "_hermes_user_memory.mnemosyne.setup",
        "_hermes_user_memory.mnemosyne.conftest",
    ):
        monkeypatch.delitem(memory.sys.modules, module_name, raising=False)

    provider = memory.load_memory_provider("mnemosyne")

    assert provider is not None
    assert provider.is_available() is True
    assert "_hermes_user_memory.mnemosyne.provider" in memory.sys.modules
    assert "_hermes_user_memory.mnemosyne.setup" not in memory.sys.modules
    assert "_hermes_user_memory.mnemosyne.conftest" not in memory.sys.modules
