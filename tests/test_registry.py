import pytest
from tabularium.registry import TableEntry, get_table, list_tables


def test_list_tables_contains_shear_strength():
    tables = list_tables()
    assert "np122.indicative_shear_strength" in tables


def test_list_tables_returns_list_of_strings():
    tables = list_tables()
    assert isinstance(tables, list)
    assert all(isinstance(k, str) for k in tables)


def test_get_table_returns_entry():
    entry = get_table("np122.indicative_shear_strength")
    assert isinstance(entry, TableEntry)
    assert entry.normative == "NP 122:2010"
    assert entry.table_id == "A.6.2"
    assert callable(entry.lookup_fn)


def test_get_table_lookup_fn_works():
    entry = get_table("np122.indicative_shear_strength")
    r = entry.lookup_fn(ip=15.0, ic=0.60, e=0.55)
    assert r.valid is True


def test_get_table_unknown_key_raises():
    with pytest.raises(KeyError, match="necunoscut"):
        get_table("np999.nonexistent")
