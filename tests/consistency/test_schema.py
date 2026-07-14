import pytest

from funkatlas import schema

pytestmark = [pytest.mark.consistency]


def test_ensure_schema_creates_all_tables(tmp_db):
    for name, _sql in schema._FACT_TABLES:
        assert schema.table_exists(tmp_db, name), name
    assert schema.table_exists(tmp_db, "migrations")
    assert schema.table_exists(tmp_db, "meta")
    for name, _sql in schema._CREATE_INDEXES:
        assert schema.index_exists(tmp_db, name), name


def test_migration_recorded_once_and_idempotent(tmp_db):
    schema.ensure_schema(tmp_db)
    schema.ensure_schema(tmp_db)
    rows = tmp_db.execute("SELECT version FROM migrations").fetchall()
    assert [r["version"] for r in rows] == [schema.SCHEMA_VERSION]


def test_now_utc_iso_is_sortable_zulu():
    ts = schema.now_utc_iso()
    assert ts.endswith("Z")
    assert ts[4] == "-" and ts[7] == "-" and ts[10] == "T" and ts[13] == ":"
    assert schema.now_utc_iso() >= ts
