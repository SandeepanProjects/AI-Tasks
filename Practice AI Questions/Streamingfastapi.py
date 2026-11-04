import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from openai import AsyncOpenAI
from pydantic import BaseModel

app = FastAPI(title="LLM Streaming API")

# Initialize the asynchronous OpenAI client
# It automatically picks up the OPENAI_API_KEY environment variable
openai_client = AsyncOpenAI()

class ChatRequest(BaseModel):
    message: str
    model: str = "gpt-4o-mini"

async def llm_stream_generator(prompt: str, model: str, request: Request):
    """
    Asynchronous generator that fetches chunks from OpenAI 
    and yields them to the FastAPI StreamingResponse.
    """
    try:
        # Request a streaming completion from the LLM provider
        response = await openai_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            stream=True  # Crucial: enables token-by-token streaming
        )

        # Iterate over the stream chunks as they arrive asynchronously
        async for chunk in response:
            # Check if the client disconnected mid-stream to free up resources
            if await request.is_disconnected():
                break
            
            # Extract content from the delta object safely
            content = chunk.choices[0].delta.content
            if content:
                yield content

    except Exception as e:
        yield f"\n[Error occurred during streaming: {str(e)}]"

@app.post("/chat/stream")
async def stream_chat(payload: ChatRequest, request: Request):
    """
    Endpoint that handles the incoming payload and returns a network stream.
    """
    # Pass the request object down so the generator can monitor disconnections
    generator = llm_stream_generator(
        prompt=payload.message, 
        model=payload.model, 
        request=request
    )
    
    # Return a StreamingResponse with the appropriate media type
    return StreamingResponse(
        generator, 
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"  # Prevents Nginx/reverse proxies from buffering the stream
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
