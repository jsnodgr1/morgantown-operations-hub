from morgantown_ops_hub.models import ActualProduction
from morgantown_ops_hub.snapshot import build_state_snapshot


def test_build_state_snapshot_smoke() -> None:
    snapshot = build_state_snapshot(
        facility_id="morgantown",
        actuals=[
            ActualProduction(
                area_id="A1",
                product_code="P100",
                quantity=42.0,
                unit="tons",
                source_id="actuals",
            )
        ],
        plans=[],
        issues=[],
    )

    assert snapshot.facility_id == "morgantown"
    assert len(snapshot.actuals) == 1
