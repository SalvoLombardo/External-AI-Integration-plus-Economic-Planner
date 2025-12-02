TASK_REGISTRY = {
    "periodic_report": {
        "endpoint": "http://localhost:5000/statistic/periodic_report",
        "prompt": (
            "You will receive the user's income and expense data "
            "for a period defined in days. Compare planned and actual expenses "
            "by category and priority, identify differences, and suggest optimization strategies. "
            "Your response must include only the information relevant to the user; "
            "do not add anything else give only the final sentence the user will see. Reply in english only"
            "go deep in your answer. Be detailed."
        )
    },
    "it_worth": {
        "endpoint": "http://localhost:5000/search_planned_transaction",
        "prompt": (
            "You will receive the amount of a planned transaction in this format "
            "{\"success\": true, \"transaction\": {\"category\": \"Something\"...etc}}, "
            "from the user. Inside the \"transaction\" key, you will find all transaction details, "
            "and the user expects to spend a certain amount for that item. "
            "If the transaction_type is an income, you can give some general advice on how to save money. "
            "Try to determine if the cost is appropriate and how they could save money. "
            "Your response must include only the information relevant to the user; "
            "do not add anything else give only the final sentence the user will see. Reply in english only"
            "go deep in your answer. Be detailed."
        )
    }
}