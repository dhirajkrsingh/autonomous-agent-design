"""
Example 1: Autonomous Agent Loop
==================================
A complete perceive-reason-plan-act-reflect cycle that runs autonomously.
The agent manages a warehouse inventory, deciding what to reorder.

Run: python examples/01_autonomous_loop.py
"""

import random


class WarehouseAgent:
    """An autonomous agent that manages warehouse inventory."""

    def __init__(self, name: str):
        self.name = name
        self.inventory = {}
        self.reorder_threshold = 10
        self.knowledge = {"avg_daily_usage": {}, "supplier_reliability": 0.9}
        self.action_log = []

    def perceive(self, sensor_data: dict):
        """Update inventory from sensor data."""
        self.inventory = sensor_data.get("stock_levels", {})
        sales = sensor_data.get("daily_sales", {})
        for item, qty in sales.items():
            history = self.knowledge["avg_daily_usage"].get(item, [])
            history.append(qty)
            if len(history) > 7:
                history = history[-7:]
            self.knowledge["avg_daily_usage"][item] = history
        print(f"  [PERCEIVE] Inventory: {self.inventory}")

    def reason(self) -> list:
        """Analyze which items need attention."""
        issues = []
        for item, qty in self.inventory.items():
            avg_usage = self._get_avg_usage(item)
            days_left = qty / avg_usage if avg_usage > 0 else 999
            if days_left < 3:
                issues.append({"item": item, "urgency": "CRITICAL", "days_left": round(days_left, 1)})
            elif qty < self.reorder_threshold:
                issues.append({"item": item, "urgency": "LOW", "days_left": round(days_left, 1)})
        print(f"  [REASON] Issues found: {len(issues)}")
        for issue in issues:
            print(f"    {issue['item']}: {issue['urgency']} ({issue['days_left']} days left)")
        return issues

    def plan(self, issues: list) -> list:
        """Create action plan based on identified issues."""
        actions = []
        for issue in issues:
            avg_usage = self._get_avg_usage(issue["item"])
            order_qty = int(avg_usage * 7)  # Order for 1 week
            if issue["urgency"] == "CRITICAL":
                actions.append({"type": "RUSH_ORDER", "item": issue["item"], "quantity": order_qty * 2})
            else:
                actions.append({"type": "STANDARD_ORDER", "item": issue["item"], "quantity": order_qty})
        print(f"  [PLAN] Actions planned: {len(actions)}")
        return actions

    def act(self, actions: list) -> list:
        """Execute planned actions."""
        results = []
        for action in actions:
            success = random.random() < self.knowledge["supplier_reliability"]
            result = {"action": action, "success": success}
            results.append(result)
            status = "SUCCESS" if success else "FAILED"
            print(f"  [ACT] {action['type']} {action['item']} x{action['quantity']} -> {status}")
            if success:
                self.inventory[action["item"]] = self.inventory.get(action["item"], 0) + action["quantity"]
        return results

    def reflect(self, results: list):
        """Learn from action outcomes."""
        failures = [r for r in results if not r["success"]]
        if failures:
            self.knowledge["supplier_reliability"] *= 0.95
            print(f"  [REFLECT] {len(failures)} failures. Adjusted supplier reliability to {self.knowledge['supplier_reliability']:.2f}")
        else:
            self.knowledge["supplier_reliability"] = min(0.99, self.knowledge["supplier_reliability"] * 1.01)
            print(f"  [REFLECT] All actions succeeded. Reliability: {self.knowledge['supplier_reliability']:.2f}")
        self.action_log.extend(results)

    def run_cycle(self, sensor_data: dict):
        """Run one complete autonomous cycle."""
        print(f"\n{'='*50}")
        self.perceive(sensor_data)
        issues = self.reason()
        if issues:
            actions = self.plan(issues)
            results = self.act(actions)
            self.reflect(results)
        else:
            print("  [REASON] No issues. All good!")

    def _get_avg_usage(self, item: str) -> float:
        history = self.knowledge["avg_daily_usage"].get(item, [3])
        return sum(history) / len(history)


if __name__ == "__main__":
    print("=== Autonomous Warehouse Agent ===")

    agent = WarehouseAgent("WarehouseBot")

    # Simulate 5 days of operation
    for day in range(1, 6):
        print(f"\n--- Day {day} ---")
        sensor_data = {
            "stock_levels": {
                "widgets": max(0, 50 - day * 12 + random.randint(-3, 3)),
                "gadgets": max(0, 30 - day * 8 + random.randint(-2, 2)),
                "bolts": max(0, 100 - day * 5 + random.randint(-5, 5)),
            },
            "daily_sales": {
                "widgets": random.randint(8, 15),
                "gadgets": random.randint(5, 10),
                "bolts": random.randint(3, 8),
            },
        }
        agent.run_cycle(sensor_data)
