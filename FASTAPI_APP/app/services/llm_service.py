import json
from openai import AsyncOpenAI
from textwrap import shorten
import os
from dotenv import load_dotenv



load_dotenv()
client=AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
import asyncio

async def send_to_llm(data, prompt):
    if isinstance(data, (bytes, str)):
        data = json.loads(data)
    if isinstance(data, dict):
        data = [data]

    chunks = chunk_data(data, max_len=1500)
    results = []

    for chunk in chunks:
        for attempt in range(3):  # fino a 3 retry
            try:
                completion = await client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "Sei un assistente AI che analizza dati finanziari personali."},
                        {"role": "user", "content": f"{prompt}\n\nDati:\n{json.dumps(chunk, ensure_ascii=False, indent=2)}"}
                    ],
                    temperature=0.4,
                )
                results.append(completion.choices[0].message.content)
                break
            except Exception as e:
                if attempt == 2:
                    raise e
                await asyncio.sleep(2)
    
    return "\n---\n".join(results)


def chunk_data(data, max_len=2000):
    json_str = json.dumps(data, ensure_ascii=False)
    if len(json_str) <= max_len:
        return [data]

    chunks, current_chunk, current_len = [], [], 0

    for item in data:
        item_len = len(json.dumps(item, ensure_ascii=False))
        if item_len > max_len:
            # Caso limite: singolo item troppo grande
            chunks.append([item])
            continue

        if current_len + item_len > max_len:
            chunks.append(current_chunk)
            current_chunk, current_len = [item], item_len
        else:
            current_chunk.append(item)
            current_len += item_len

    if current_chunk:
        chunks.append(current_chunk)
    return chunks