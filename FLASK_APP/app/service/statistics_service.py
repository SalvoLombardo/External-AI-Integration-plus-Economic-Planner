from datetime import datetime

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from app.service.transaction_service import get_all_actual_trans,get_all_plann_trans
from app.service.wallet_service import get_all_accounts
from app.models import PlannedTransaction, ActualTransaction
from app.schemas.statistics_schemas import GetOnlyDateSchema, GetDaysPrevision

from app.extensions import db



#-------------------------------
#FORECAST SECTION
#-------------------------------
def calculate_forecast(trans, validated: GetOnlyDateSchema, transaction_type:str, today=None):
    ## - Here there's the core function to calculate the amount of every transaction
    ##   and if it's recurring, so to calculate how many times occurs and calculate the sum
    
    today = today or datetime.now().date()
    end_date = validated.end_prevision

    ## - Here the function get the transaction type (planned or actual) and after ger the single amount and the sart date.
    ##   **(IMPORTANT) The start date is when the transaction was happened, in case of a recurring transaction, this is the
    ##          selected day of recurring. 
    ##          Ex: if it's monday 2025/01/01, during the calculation if it's weekly for ex it will calculate every 7 days and so on

    if transaction_type == "planned":
        amount = trans.planned_amount
        start_date = trans.planned_date_start
    elif transaction_type == "actual":
        amount = trans.actual_amount
        start_date = trans.actual_date_start
    else:
        raise ValueError("amount_type deve essere 'planned' o 'actual'")

    if not start_date:
        return 0

    start_date = start_date.date() if isinstance(start_date, datetime) else start_date

    ## Here the func check if is recurring, if not return the single amount
    if not trans.recurring:
        return amount if start_date <= end_date else 0

    freq = trans.frequency.value
    total = 0

    ##-------------------------------(DAILY)
    ##    Each recurrence adds 1 day → calculate total days between next valid occurrence and end date.
    if freq == "daily":
        days_diff = (today - start_date).days
        next_occurrence = start_date + timedelta(days=(days_diff + 1))
        occurrences = (end_date - next_occurrence).days + 1
        total = max(0, occurrences) * amount

    ##-------------------------------(WEEKLY)
    ##    Similar to daily, but works in blocks of 7 days (1 week = 7 days).
    ##    The division by 7 converts days into full weeks.
    elif freq == "weekly":
        weeks_diff = (today - start_date).days // 7
        next_occurrence = start_date + timedelta(weeks=(weeks_diff + 1))
        occurrences = ((end_date - next_occurrence).days // 7) + 1
        total = max(0, occurrences) * amount


    ##-------------------------------(MONTHLY)
    ##    Uses relativedelta to correctly handle months with different lengths.
    ##    Formula:
    ##       months_diff = months between start_date and today
    ##       next_occurrence = start_date + months_diff
    ##       total months = months between next_occurrence and end_date
    elif freq == "monthly":
        months_diff = (today.year - start_date.year) * 12 + (today.month - start_date.month)
        if today.day >= start_date.day:
            months_diff += 1
        next_occurrence = start_date + relativedelta(months=months_diff)
        months_until_end = (end_date.year - next_occurrence.year) * 12 + (end_date.month - next_occurrence.month)
        total = max(0, months_until_end + 1) * amount


    ##-------------------------------(YEARLY)
    ##    Works exactly like monthly, but using years as units.
    ##    Uses tuple comparison to handle month/day boundaries correctly.
    elif freq == "yearly":
        years_diff = today.year - start_date.year
        
        if (today.month, today.day) >= (start_date.month, start_date.day):
            years_diff += 1
        next_occurrence = start_date + relativedelta(years=years_diff)

        years_until_end = end_date.year - next_occurrence.year
        total = max(0, years_until_end + 1) * amount

    return total


def calculate_planned_user_forecast(user_id: int, validated: GetOnlyDateSchema):
    ## - In this service function i create 2 variables to get a sum of the all results of the calculate_forcast funciton
    ##   to have only one function i pass a keword to the calculate_forcast funciton like 'planned' or 'actual'
    ##   This is crucial beacuse to access into the ORM obj we have to differenciate the attribute.
    #########IMPORTANT:
                     #Here we calculate planned and actual transaction so still remains a planned prevision
                     #the actual prevision(down below) takes only real transaction.

    planned_trans = get_all_plann_trans(user_id) or []
    actual_trans = get_all_actual_trans(user_id) or []

    outcome = 0
    income = 0

    for plan_trans in planned_trans:
        if not plan_trans.is_completed:#(*IMPORTANT)see below
            if plan_trans.transaction_type.value == 'outcome':
                outcome += calculate_forecast(plan_trans, validated, 'planned')
            elif plan_trans.transaction_type.value == 'income':
                income += calculate_forecast(plan_trans, validated, 'planned')
                                    #* A planned transaction, when the user confirm the transaction
                                    #  became an Actual Transaction, so in the db we have 2 transactions with the same
                                    #  or similar amout(and also other details).
                                    #  The previous Planned Transaction became 'is_completed'==True so in this way
                                    #  the function can skip to not get a duplicate-ish transaction.


    for act_trans in actual_trans:
        if act_trans.transaction_type.value == 'outcome':
            outcome += calculate_forecast(act_trans, validated, 'actual')
        elif act_trans.transaction_type.value == 'income':
            income += calculate_forecast(act_trans, validated, 'actual')

    #Get all accounts(bank account,credit card ecc) and sum them all
    all_accounts = get_all_accounts(user_id) or []
    all_current_balance = sum(account.current_balance for account in all_accounts)

    total_forecast = all_current_balance + income - outcome

    return {
        "current_balance": all_current_balance,
        "planned_income": income,
        "planned_outcome": outcome,
        "total_forecast": total_forecast
    }


def calculate__actual_user_forecast(user_id: int, validated: GetOnlyDateSchema):
    ## To understand this function you can see the calculate_planned_user_forecast up above
    ## is the same funcion but based in 2 diffrent situation: planned prevision and actual/real prevision
    
    
    actual_trans = get_all_actual_trans(user_id) or []

    outcome = 0
    income = 0

    for act_trans in actual_trans:
        if act_trans.transaction_type.value == 'outcome':
            outcome += calculate_forecast(act_trans, validated, 'actual')
        elif act_trans.transaction_type.value == 'income':
            income += calculate_forecast(act_trans, validated, 'actual')

    all_accounts = get_all_accounts(user_id) or []
    all_current_balance = sum(account.current_balance for account in all_accounts)


    total_forecast = all_current_balance + income - outcome

    return {
        "current_balance": all_current_balance,
        "actual_income": income,
        "actual_outcome": outcome,
        "total_forecast": total_forecast
    }



#-------------------------------
#CALCULATE OCCURRENCES SECTION
#-------------------------------
def calculate_occurrences(trans, validated, amount_type: str, today=None):
    #  This function is pretty similar to def calculate_forecast(up above) but is more focused on
    #  getting every transaction and return how many times happen and some other info.
    #  It's also based on some defined time period.

    today = today or datetime.now().date()
    days = validated.days
    target_day = today - timedelta(days=days)

    # Importo e data di partenza
    if amount_type == "planned":
        amount = trans.planned_amount
        start_date = trans.planned_date_start
    elif amount_type == "actual":
        amount = trans.actual_amount
        start_date = trans.actual_date_start
    else:
        raise ValueError("amount_type deve essere 'planned' o 'actual'")

    if not start_date:
        return  None
    if start_date > today :
        return  None

    if not trans.recurring:
        return {
            "Occurrences": 1 if start_date <= today else 0,
            "Amount": amount,
            "Title": trans.title,
            "Category": trans.category.name if trans.category else None,
            "SubCategory": trans.sub_category.name if trans.sub_category else None,
        }

    freq = trans.frequency.value

    if freq == "daily":
        occurrences = days

    elif freq == "weekly":
        weeks_diff = ((target_day - start_date).days // 7) + 1
        next_payday_after_target_date = start_date + timedelta(weeks=weeks_diff)
        diff_days = (next_payday_after_target_date - target_day).days
        occurrences = (days + diff_days) // 7

    else:
        occurrences = 0  #Da fare : aggiungere monthly, yearly ecc.

    return {
    "number_of_occurrences": occurrences,
    "amount": float(amount or 0),
    "title": trans.title,
    "category": trans.category.name if trans.category else None,
    "sub_category": trans.sub_category.name if trans.sub_category else None,
    "priority_score": trans.priority_score,
}






