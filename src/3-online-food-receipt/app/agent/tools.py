import json
from datetime import date

from langchain_core.tools import BaseTool, tool

from app.use_cases.query_receipt import SearchReceipts, SearchReceiptsInput, SumExpenses


def build_tools(search_receipts: SearchReceipts, sum_expenses: SumExpenses) -> list[BaseTool]:
    @tool
    def search_food_receipts(
        start_date: str | None = None,
        end_date: str | None = None,
        food_name: str | None = None,
        place: str | None = None,
    ) -> str:
        """Search the user's uploaded food receipts, optionally filtered by a transaction
        date range (ISO format YYYY-MM-DD), a food/item name, and/or the place purchased
        from. Returns matching receipts with their line items as JSON. Use this to answer
        questions about what was bought, when, and where."""
        result = search_receipts.execute(
            SearchReceiptsInput(
                start_date=date.fromisoformat(start_date) if start_date else None,
                end_date=date.fromisoformat(end_date) if end_date else None,
                food_name=food_name,
                place=place,
            )
        )
        return json.dumps([r.model_dump(mode="json") for r in result])

    @tool
    def sum_food_expenses(
        start_date: str | None = None,
        end_date: str | None = None,
        food_name: str | None = None,
        place: str | None = None,
    ) -> str:
        """Compute the exact total amount spent on food, optionally filtered by a
        transaction date range (ISO format YYYY-MM-DD), a food/item name, and/or the place
        purchased from. Always call this tool for totals/sums instead of adding numbers up
        yourself."""
        total = sum_expenses.execute(
            SearchReceiptsInput(
                start_date=date.fromisoformat(start_date) if start_date else None,
                end_date=date.fromisoformat(end_date) if end_date else None,
                food_name=food_name,
                place=place,
            )
        )
        return json.dumps({"total": total})

    return [search_food_receipts, sum_food_expenses]
