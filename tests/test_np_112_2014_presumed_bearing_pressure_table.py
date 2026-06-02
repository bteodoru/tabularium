import pytest
from tabularium.np_112_2014.presumed_bearing_pressure.table import get_p_conv_table


def test_returns_three_families():
    result = get_p_conv_table()
    families = [f.soil_family for f in result.families]
    assert set(families) == {"boulders_gravels", "sands", "fines"}


def test_boulders_gravels_has_six_categories():
    result = get_p_conv_table()
    bg = next(f for f in result.families if f.soil_family == "boulders_gravels")
    assert len(bg.categories) == 6


def test_interpolable_categories_have_required_params():
    result = get_p_conv_table()
    bg = next(f for f in result.families if f.soil_family == "boulders_gravels")
    cat_map = {c.soil_category: c for c in bg.categories}
    assert "consistency_index" in cat_map["boulder_cohesive_fill"].required_params
    assert "consistency_index" in cat_map["gravel_clayey_sand"].required_params


def test_fixed_categories_have_no_required_params():
    result = get_p_conv_table()
    bg = next(f for f in result.families if f.soil_family == "boulders_gravels")
    cat_map = {c.soil_category: c for c in bg.categories}
    assert cat_map["boulder_gravel_fill"].required_params == []
    assert cat_map["gravel_with_sand"].required_params == []


def test_sands_has_four_categories():
    result = get_p_conv_table()
    sands = next(f for f in result.families if f.soil_family == "sands")
    assert len(sands.categories) == 4


def test_sands_fine_and_silty_require_moisture():
    result = get_p_conv_table()
    sands = next(f for f in result.families if f.soil_family == "sands")
    cat_map = {c.soil_category: c for c in sands.categories}
    assert "moisture_condition" in cat_map["fine_sand"].required_params
    assert "moisture_condition" in cat_map["silty_sand"].required_params


def test_fines_family_has_no_categories_but_required_params():
    result = get_p_conv_table()
    fines = next(f for f in result.families if f.soil_family == "fines")
    assert fines.categories == []
    assert set(fines.required_params) == {"plasticity_class", "void_ratio", "consistency_index"}


def test_soil_labels_are_romanian_strings():
    result = get_p_conv_table()
    bg = next(f for f in result.families if f.soil_family == "boulders_gravels")
    labels = [c.soil_label for c in bg.categories]
    assert "Pietriș cu nisip" in labels
    assert "Nisip" not in labels  # nisipurile sunt în familia sands


def test_to_dict_excludes_empty_required_params():
    result = get_p_conv_table()
    bg = next(f for f in result.families if f.soil_family == "boulders_gravels")
    cat_map = {c.soil_category: c for c in bg.categories}
    d = cat_map["boulder_gravel_fill"].to_dict()
    assert "required_params" not in d


def test_to_dict_includes_required_params_when_present():
    result = get_p_conv_table()
    bg = next(f for f in result.families if f.soil_family == "boulders_gravels")
    cat_map = {c.soil_category: c for c in bg.categories}
    d = cat_map["boulder_cohesive_fill"].to_dict()
    assert d["required_params"] == ["consistency_index"]
