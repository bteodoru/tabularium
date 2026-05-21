import pytest
from tabularium.registry import REGISTRY, TableEntry, get_table, list_tables
from tabularium.np_122_2010.indicative_deformation_modulus_non_cohesive import (
    RelativeDensity,
    SoilCategory,
)


def test_list_tables_contains_shear_strength():
    tables = list_tables()
    assert "np_122_2010.indicative_shear_strength" in tables


def test_list_tables_returns_list_of_strings():
    tables = list_tables()
    assert isinstance(tables, list)
    assert all(isinstance(k, str) for k in tables)


def test_get_table_returns_entry():
    entry = get_table("np_122_2010.indicative_shear_strength")
    assert isinstance(entry, TableEntry)
    assert entry.normative == "NP 122:2010"
    assert entry.table_id == "A.6.2"
    assert callable(entry.lookup_fn)


def test_get_table_lookup_fn_works():
    entry = get_table("np_122_2010.indicative_shear_strength")
    r = entry.lookup_fn(ip=15.0, ic=0.60, e=0.55)
    assert r.valid is True


def test_get_table_unknown_key_raises():
    with pytest.raises(KeyError, match="necunoscut"):
        get_table("np999.nonexistent")


def test_registry_has_non_cohesive_deformation_modulus():
    assert "np_122_2010.indicative_deformation_modulus_non_cohesive" in REGISTRY


def test_registry_has_cohesive_deformation_modulus():
    assert "np_122_2010.indicative_deformation_modulus_cohesive" in REGISTRY


def test_registry_non_cohesive_entry_metadata():
    entry = get_table("np_122_2010.indicative_deformation_modulus_non_cohesive")
    assert entry.normative == "NP 122:2010"
    assert entry.table_id == "A.6.3"
    assert callable(entry.lookup_fn)


def test_registry_cohesive_entry_metadata():
    entry = get_table("np_122_2010.indicative_deformation_modulus_cohesive")
    assert entry.normative == "NP 122:2010"
    assert entry.table_id == "A.6.4"
    assert callable(entry.lookup_fn)


def test_registry_cohesive_lookup_fn_works():
    entry = get_table("np_122_2010.indicative_deformation_modulus_cohesive")
    r = entry.lookup_fn(ip=15.0, ic=0.80, e=0.55)
    assert r.valid is True


def test_registry_non_cohesive_lookup_fn_works():
    entry = get_table("np_122_2010.indicative_deformation_modulus_non_cohesive")
    r = entry.lookup_fn(SoilCategory.FINE_SAND, RelativeDensity.MEDIUM)
    assert r.valid is True
