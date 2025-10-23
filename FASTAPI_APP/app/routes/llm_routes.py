# app/routers/llm_router.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator
from app.services.llm_service import send_to_llm
from app.pydantic_models.llm_models import UserTokenTaskDataSchema
import httpx
import os

from app.utils.task_registry import TASK_REGISTRY

ai_router = APIRouter(prefix='/ai')



@ai_router.post("/ai_process")
async def ai_process(user_token_and_task: UserTokenTaskDataSchema):
    #In this route the Front-end pass the token given by the backend during the login and pass also 
    # the specific tast that AI have to do.
    #We have a disctionary of tasks (see from app.utils.task_registry import TASK_REGISTRY)
    #Every task is connected with a Flask endpoint.
    #The process is FastApi->request to Flask -> tokenvalidation and flask function->again to FastApi to sand result to LLM and elaborate them



    #Check if front end pass the right task
    if user_token_and_task.task not in TASK_REGISTRY:
        raise HTTPException(status_code=400, detail="invalid task")
    
    #Getting the single task with his 'prompt' and 'endpoint'
    single_task= TASK_REGISTRY[user_token_and_task.task]
    
    #Getting the URL and create the headers
    FLASK_URL=single_task.get('endpoint')
    headers = {"Authorization": f"Bearer {user_token_and_task.user_jwt_token}"}
    
    
    #Getting the data that will pass in the endpoint
    #IMPORTANT: see how it's described the UserTokenTaskDataSchema
    #           'data' is every type of data format
    payload= user_token_and_task.data
    


    #Connecting to the endpoint with httpx.AsyncClient because 'requests' doesn't support async.
    try:
        async with httpx.AsyncClient() as client:
            flask_response = await client.post(
                FLASK_URL, 
                headers=headers,
                json=payload,
                timeout=10
                )
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Errore di connessione a Flask: {e}")
    
    
    #Here we handle errors and propagate error messages to FAstAPI
    if flask_response.status_code != 200:
        try:
            flask_error = flask_response.json()
        except Exception:
            flask_error = {"detail": flask_response.text}

        raise HTTPException(
            status_code=flask_response.status_code,
            detail={
                "source": "flask",
                "message": flask_error
            }
        )
    
  
    data =flask_response.json()
    if not data:
        raise HTTPException(status_code=500, detail="Flask response vuota o non valida")


    prompt=single_task.get('prompt')
    
    # passa data to llm with the promp got by single_task
    llm_result = await send_to_llm(data,prompt)

    return {"llm_result": llm_result}