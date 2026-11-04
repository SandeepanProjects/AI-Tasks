import asyncio
import time
import random

# A robust wrapper function to handle retries for individual agents
async def run_agent_with_retry(agent_id: int, prompt: str, max_retries: int = 3, backoff_factor: float = 2.0) -> dict:
    attempt = 0
    delay = 1.0  # Initial wait time before the first retry (in seconds)
    
    while True:
        try:
            attempt += 1
            # Call the core agent logic
            return await run_agent(agent_id, prompt, attempt)
            
        except Exception as e:
            if attempt >= max_retries:
                print(f"❌ [Agent {agent_id}] Failed permanently after {max_retries} attempts.")
                raise e  # Propagate the error up to asyncio.gather
            
            # Apply exponential backoff with a bit of randomness (jitter) to prevent hammering the API
            jitter = random.uniform(0.1, 0.5)
            current_delay = (delay * backoff_factor) + jitter
            
            print(f"⚠️ [Agent {agent_id}] Attempt {attempt} failed: {e}. Retrying in {current_delay:.2f}s...")
            await asyncio.sleep(current_delay)
            delay = current_delay  # Update base delay for the next loop

# Core agent logic
async def run_agent(agent_id: int, prompt: str, attempt: int) -> dict:
    print(f"[Agent {agent_id}] Executing task (Attempt {attempt}): '{prompt}'")
    await asyncio.sleep(1.0)  # Simulate network/LLM latency
    
    # Simulating standard production issues:
    # Let's make Agent 2 fail its first two attempts, but succeed on its 3rd attempt.
    if agent_id == 2 and attempt < 3:
        raise RuntimeError("API Rate limit hit (429)")
        
    response = f"Success! Result for: '{prompt}'"
    return {"agent_id": agent_id, "status": "success", "response": response}

async def main():
    # Wrap our agents inside the retry handler
    tasks = [
        run_agent_with_retry(agent_id=1, prompt="Analyze codebase security."),
        run_agent_with_retry(agent_id=2, prompt="Write unit tests for auth."),  # Flaky agent
        run_agent_with_retry(agent_id=3, prompt="Generate API documentation."),
    ]

    start_time = time.time()
    
    # Keep return_exceptions=True as a final safety net for catastrophic errors
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    elapsed_time = round(time.time() - start_time, 2)
    print(f"\nPipeline finished in {elapsed_time} seconds.\n")
    
    for idx, res in enumerate(results, start=1):
        if isinstance(res, Exception):
            print(f"❌ [Agent {idx}] CRITICAL FAILURE: {res}")
        else:
            print(f"✅ [Agent {idx}] RESPONSE: {res['response']}")

if __name__ == "__main__":
    asyncio.run(main())
