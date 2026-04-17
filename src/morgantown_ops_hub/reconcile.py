"""Reconciliation logic for plan-versus-actual operating state."""

from __future__ import annotations

from morgantown_ops_hub.models import ActualProduction, Issue, PlanTarget, Severity


def reconcile_schedule_vs_actual(
    actuals: list[ActualProduction],
    plans: list[PlanTarget],
    tolerance_ratio: float = 0.10,
) -> list[Issue]:
    """Generate issues for missing or materially different plan/actual records."""
    issues: list[Issue] = []
    plan_index = {
        (plan.area_id, plan.product_code, plan.period): plan
        for plan in plans
    }

    for actual in actuals:
        key = (actual.area_id, actual.product_code, "daily")
        matching_plan = plan_index.get(key)
        if matching_plan is None:
            issues.append(
                Issue(
                    code="missing_daily_plan",
                    message="No matching daily plan target was found for actual production.",
                    severity=Severity.WARNING,
                    source_id=actual.source_id,
                    context={"area_id": actual.area_id, "product_code": actual.product_code},
                )
            )
            continue

        if matching_plan.quantity == 0:
            continue

        variance_ratio = abs(actual.quantity - matching_plan.quantity) / matching_plan.quantity
        if variance_ratio > tolerance_ratio:
            issues.append(
                Issue(
                    code="plan_actual_variance",
                    message="Actual production differs materially from the daily plan target.",
                    severity=Severity.WARNING,
                    source_id=actual.source_id,
                    context={
                        "area_id": actual.area_id,
                        "product_code": actual.product_code,
                        "actual_quantity": actual.quantity,
                        "planned_quantity": matching_plan.quantity,
                    },
                )
            )

    return issues
