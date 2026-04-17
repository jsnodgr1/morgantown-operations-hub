from morgantown_ops_hub.models import ActualProduction, PlanTarget
from morgantown_ops_hub.reconcile import reconcile_schedule_vs_actual


def test_reconcile_schedule_vs_actual_smoke() -> None:
    actuals = [
        ActualProduction(
            area_id="A1",
            product_code="P100",
            quantity=100.0,
            unit="tons",
            source_id="actuals",
        )
    ]
    plans = [
        PlanTarget(
            area_id="A1",
            product_code="P100",
            quantity=100.0,
            unit="tons",
            period="daily",
            source_id="schedule",
        )
    ]

    issues = reconcile_schedule_vs_actual(actuals, plans)

    assert issues == []
