from app.extensions import db
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.service.transaction_service import get_all_plann_trans,get_all_actual_trans
from app.service.statistics_service import calculate_forecast,calculate_planned_user_forecast, calculate__actual_user_forecast, calculate_occurrences
from app.service.wallet_service import get_all_accounts

from pydantic import ValidationError
from app.schemas.statistics_schemas import GetOnlyDateSchema, GetDaysPrevision

statistics = Blueprint('statistics', __name__)
#-------------------------------
# STATISTICS AND PREVISIONS 
#-------------------------------

@statistics.post('/get_planned_prevision')
@jwt_required()
def get_planned_prevision():
    #Used to get a prevision about only planned transactions, filtering by a date in the future
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    #Using pydantic to validate data
    try:
        validated=GetOnlyDateSchema(**data) 
    except ValidationError as e:
        return jsonify({'errors':e.errors()}), 400
    

    result = calculate_planned_user_forecast(user_id, validated)
    return jsonify({
        "Total prevision": result["total_forecast"],
        "Details": {
            "Current balance": result["current_balance"],
            "Planned income": result["planned_income"],
            "Planned outcome": result["planned_outcome"]
        }
    }), 200

@statistics.post('/get_actual_prevision')
@jwt_required()
def get_actual_prevision():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    try:
        validated=GetOnlyDateSchema(**data)
    except ValidationError as e:
        return jsonify({'errors':e.errors()}), 400
    
    
    result = calculate__actual_user_forecast(user_id, validated)
    return jsonify({
        "Total prevision": result["total_forecast"],
        "Details": {
            "Current balance": result["current_balance"],
            "Actual income": result["actual_income"],
            "Actual outcome": result["actual_outcome"]
        }
    }), 200


@statistics.post('/save_money_with_prevision')
@jwt_required()
def save_money_with_prevision():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}



    try:
        validated=GetOnlyDateSchema(**data)
    except ValidationError as e:
        return jsonify({'Errors': e.errors()}), 400
    


    
    all_planned_trans = get_all_plann_trans(user_id) or []
    non_urgent_outcome_planned = 0
    for trans in all_planned_trans:
        if getattr(trans.priority_score, "value", trans.priority_score) == 3 and trans.transaction_type.value == 'outcome' and not trans.is_completed:
            non_urgent_outcome_planned += calculate_forecast(trans, validated, 'planned')

    
    all_actual_trans = get_all_actual_trans(user_id) or []
    non_urgent_outcome_actual = 0
    for trans in all_actual_trans:
        if getattr(trans.priority_score, "value", trans.priority_score) == 3 and trans.transaction_type.value == 'outcome':
            non_urgent_outcome_actual += calculate_forecast(trans, validated, 'actual')

    total_non_urgent = non_urgent_outcome_actual + non_urgent_outcome_planned

    # usa la funzione riutilizzabile per ottenere la previsione principale
    prevision = calculate_planned_user_forecast(user_id, validated)
    current_total = prevision["total_forecast"]

    # Qui interpreti il risultato come vuoi:
    # se vuoi sapere quanto puoi mettere da parte, togli le spese non urgenti:
    can_save = current_total + total_non_urgent  # (o qualche altra logica)

    # restituisci un messaggio leggibile
    return jsonify({
        "end_prevision": validated.end_prevision,
        "current_forecast": current_total,
        "total_non_urgent": total_non_urgent,
        "can_save_if_deferrable": can_save
    }), 200
    


@statistics.post('/low_priority_outcome')
@jwt_required()
def low_priority_outcome():
    user_id = int(get_jwt_identity())
    

    all_planned_trans=get_all_plann_trans(user_id)
    non_urgent_outcome=0
    for trans in all_planned_trans:
        if trans.priority_score.value==3 and trans.transaction_type.value=='outcome':
            non_urgent_outcome+=trans.planned_amount

    return jsonify({"You can save":non_urgent_outcome})





@statistics.post('/statistic/periodic_report')
@jwt_required()
def periodic_report():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}



    try:
        validated=GetDaysPrevision(**data)
    except ValidationError as e:
        return jsonify({'Errors': e.errors()}), 400
    

    all_planned_trans=get_all_plann_trans(user_id)
    all_actual_trans=get_all_actual_trans(user_id)

    single_planned_trans_outcome = []
    single_planned_trans_income = []
    single_actual_trans_outcome = []
    single_actual_trans_income = []

    for p_trans in all_planned_trans or []:
        if not p_trans.is_completed:
            if p_trans.transaction_type.value == 'outcome':
                single_planned_trans_outcome.append(calculate_occurrences(p_trans,validated,'planned'))
            elif p_trans.transaction_type.value == 'income':
                single_planned_trans_income.append(calculate_occurrences(p_trans,validated,'planned'))
       


    for a_trans in all_actual_trans or []:
        if a_trans.transaction_type.value == 'outcome':
            single_actual_trans_outcome.append(
                calculate_occurrences(a_trans, validated, 'actual')
            )
        elif a_trans.transaction_type.value == 'income':
            single_actual_trans_income.append(
                calculate_occurrences(a_trans, validated, 'actual')
            )

    return jsonify({
        "planned_outcome": single_planned_trans_outcome,
        "planned_income": single_planned_trans_income,
        "actual_outcome": single_actual_trans_outcome,
        "actual_income": single_actual_trans_income
    })


    
    


    
    



