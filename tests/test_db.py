from capstone import db

def test_query():
    assert db.db.query("SELECT 1 as x").list() == [{"x": 1}]