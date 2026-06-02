import pytest
from tabularium.registry import registry
from tabularium.core.registry import TableEntry
from tabularium.enums import RelativeDensity, Soil


def test_registry_contains_all_expected_keys():
    keys = set(registry.all())
    expected = {
        "np_122_2010.indicative_shear_strength_non_cohesive",
        "np_122_2010.indicative_shear_strength_cohesive",
        "np_122_2010.indicative_deformation_modulus_non_cohesive",
        "np_122_2010.indicative_deformation_modulus_cohesive",
        "np_112_2014.presumed_bearing_pressure_rocks",
        "np_112_2014.presumed_bearing_pressure_boulders",
        "np_112_2014.presumed_bearing_pressure_gravels",
        "np_112_2014.presumed_bearing_pressure_sands",
        "np_112_2014.presumed_bearing_pressure_fines",
        "np_112_2014.presumed_bearing_pressure_fills",
        "np_112_2014.working_condition_factor",
    }
    assert expected.issubset(keys)


def test_get_returns_table_entry():
    entry = registry.get("np_122_2010.indicative_shear_strength_cohesive")
    assert isinstance(entry, TableEntry)
    assert entry.normative == "NP 122:2010"
    assert entry.table_id == "A.6.2"
    assert callable(entry.func)


def test_get_unknown_key_raises():
    with pytest.raises(KeyError, match="necunoscut"):
        registry.get("np999.nonexistent")


def test_func_is_callable_and_returns_valid_result():
    entry = registry.get("np_122_2010.indicative_shear_strength_cohesive")
    result = entry.func(ip=15.0, ic=0.60, e=0.55)
    assert result.valid is True


def test_all_returns_dict_of_table_entries():
    all_tables = registry.all()
    assert isinstance(all_tables, dict)
    assert all(isinstance(v, TableEntry) for v in all_tables.values())


def test_np122_deformation_non_cohesive_entry():
    entry = registry.get("np_122_2010.indicative_deformation_modulus_non_cohesive")
    assert entry.normative == "NP 122:2010"
    assert entry.table_id == "A.6.3"
    result = entry.func(Soil.FINE_SAND, RelativeDensity.MEDIUM)
    assert result.valid is True


def test_np122_deformation_cohesive_entry():
    entry = registry.get("np_122_2010.indicative_deformation_modulus_cohesive")
    assert entry.normative == "NP 122:2010"
    assert entry.table_id == "A.6.4"
    result = entry.func(ip=15.0, ic=0.80, e=0.55)
    assert result.valid is True


def test_np112_sands_entry_metadata():
    entry = registry.get("np_112_2014.presumed_bearing_pressure_sands")
    assert entry.normative == "NP 112:2014"
    assert entry.table_id == "D.3"
    assert callable(entry.func)
