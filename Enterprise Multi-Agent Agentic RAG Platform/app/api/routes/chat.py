from fastapi import APIRouter

from app.schemas.request import ChatRequest

from app.schemas.response import ChatResponse

from app.services.chat_service import ask_question


router = APIRouter()


@router.post(
    "/chat",
    response_model=ChatResponse
)
def chat(request: ChatRequest):

    answer = ask_question(
        request.question
    )

    return ChatResponse(
        answer=answer
    )