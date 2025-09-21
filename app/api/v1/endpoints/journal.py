from fastapi import Depends, APIRouter, HTTPException
from ...deps import get_current_user
from ....schemas.journal import JournalRequest, JournalResponse
from ....core.config import settings
from openai import OpenAI

router = APIRouter()
client = OpenAI(api_key=settings.OPENAI_API_KEY)


@router.post("/", response_model=JournalResponse)
async def process_journal(
        journal: JournalRequest,
        current_user = Depends(get_current_user)
):
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role":"system", "content": "You are a nmin"}
            ]
        )

        ai_text = completion.choices[0].message.content or ""
        suggestions = [
            line.replace(".", "").strip()
            for line in ai_text.split("\n")
            if line.strip()
        ]

        return JournalResponse(suggestions=suggestions)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))