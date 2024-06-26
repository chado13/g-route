from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Body, Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from server.deps import get_assistant

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter()


class TripData(BaseModel):
    destination: str = Field(examples=["서울"])
    schedule: list[datetime]
    spots: str
    hotel: str | None
    arrival: str | None
    depart: str | None
    transport: str
    restorants: str


class AssistantResponse(BaseModel):
    assistant_id: str
    thread_id: str


@app.get("/groute/assistant")
def get(user_id: int, assistant=Depends(get_assistant)) -> AssistantResponse:
    return AssistantResponse(
        assistant_id=assistant.assistant_id, thread_id=assistant.thread_id
    )


@app.post("/groute")
def send_message(data: Annotated[TripData, Body], assistant=Depends(get_assistant)):
    content = (
        f"{data.destination}의 {data.spots}을  {data.schedule[0]} 부터 {data.schedule[1]}까지의 일정으로 여행할 예정입니다. "
        f"{data.arrival}에 도착하여 일정을 시작하여 {data.depart}에서 돌아갈 예정입니다."
        f"여행일정 내내 {data.hotel}에서 숙박할 예정이고 {data.restorants}들에서 식사할 예정입니다."
        f"주요 이동수단으로는 {data.transport}를 이용할 예정입니다."
    )
    assistant.send_message(content)
    message = assistant.run_assistant()
    return message
