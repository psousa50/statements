from src.app.common.json_utils import is_json, sanitize_json


def test_sanitize_json():
    assert sanitize_json('{"a": 1}') == {"a": 1}
    assert sanitize_json("not json") is None


def test_is_json():
    assert is_json('{"a": 1}')
    assert not is_json("not json")
