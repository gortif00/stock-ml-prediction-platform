import os

from mcp_server.scripts import DEFAULT_SYMBOLS
from mcp_server.scripts.assets import get_symbols, resolve_symbol


def test_resolve_symbol_aliases():
    assert resolve_symbol("IBEX35") == "^IBEX"
    assert resolve_symbol("^GSPC") == "^GSPC"


def test_get_symbols_default(monkeypatch):
    monkeypatch.delenv("SYMBOLS", raising=False)
    monkeypatch.delenv("MARKETS", raising=False)
    assert get_symbols() == list(DEFAULT_SYMBOLS)


def test_get_symbols_from_env(monkeypatch):
    monkeypatch.setenv("SYMBOLS", "IBEX35, ^GSPC")
    assert get_symbols() == ["^IBEX", "^GSPC"]
