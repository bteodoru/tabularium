from tabularium.models import CodeSource, LookupResult


def test_code_source_required_fields():
    src = CodeSource(code="NP 122:2010", table="Tabelul A.6.2")
    assert src.code == "NP 122:2010"
    assert src.table == "Tabelul A.6.2"
    assert src.section is None


def test_code_source_with_section():
    src = CodeSource(code="NP 122:2010", table="Tabelul A.6.2", section="A.6")
    assert src.section == "A.6"


def test_lookup_result_defaults():
    r = LookupResult()
    assert r.valid is False
    assert r.interpolated is False
    assert r.source is None
    assert r.warnings == []
    assert r.errors == []


def test_lookup_result_with_source():
    src = CodeSource(code="NP 122:2010", table="Tabelul A.6.2")
    r = LookupResult(valid=True, source=src)
    assert r.valid is True
    assert r.source.code == "NP 122:2010"


def test_lookup_result_warnings_not_shared():
    r1 = LookupResult()
    r2 = LookupResult()
    r1.warnings.append("w")
    assert r2.warnings == []
