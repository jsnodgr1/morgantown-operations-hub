from morgantown_ops_hub.normalize import normalize_headers


def test_normalize_headers_smoke() -> None:
    assert normalize_headers([" Area Name ", "Daily Target (Tons)"]) == [
        "area_name",
        "daily_target_tons",
    ]
