import pytest
from tabularium.core.registry import Registry, TableEntry


def _entry(name: str = "t") -> TableEntry:
    return TableEntry(
        func=lambda: None,
        normative="NP 999:2099",
        table_id="X.1",
        description=f"Test {name}",
    )


def test_register_and_get():
    reg = Registry()
    e = _entry()
    reg.register("test", e)
    assert reg.get("test") is e


def test_get_unknown_raises_key_error():
    reg = Registry()
    with pytest.raises(KeyError, match="necunoscut"):
        reg.get("nonexistent")


def test_all_returns_shallow_copy():
    reg = Registry()
    e = _entry()
    reg.register("t", e)
    result = reg.all()
    assert result == {"t": e}
    result["extra"] = _entry("extra")
    assert "extra" not in reg.all()


def test_include_without_namespace():
    reg = Registry()
    other = Registry()
    e = _entry()
    other.register("foo", e)
    reg.include(other)
    assert reg.get("foo") is e


def test_include_with_namespace():
    reg = Registry()
    other = Registry()
    e = _entry()
    other.register("foo", e)
    reg.include(other, namespace="np_999_2099")
    assert reg.get("np_999_2099.foo") is e
    with pytest.raises(KeyError):
        reg.get("foo")


def test_include_does_not_mutate_source():
    reg = Registry()
    other = Registry()
    e = _entry()
    other.register("foo", e)
    reg.include(other, namespace="ns")
    assert reg.all() == {"ns.foo": e}
    assert other.all() == {"foo": e}


def test_table_entry_fields():
    fn = lambda: None
    e = TableEntry(func=fn, normative="NP 1:2000", table_id="A.1", description="x")
    assert e.func is fn
    assert e.normative == "NP 1:2000"
    assert e.table_id == "A.1"
    assert e.description == "x"
