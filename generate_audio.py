import asyncio, json, os
import edge_tts

VOICE = "de-DE-KatjaNeural"
OUT_DIR = "audio"

async def gen(text, path):
    if os.path.exists(path):
        return
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save(path)

async def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    with open('tts_content.json', encoding='utf-8') as f:
        data = json.load(f)

    tasks = []
    for i, p in enumerate(data['passages']):
        for j, (de, en) in enumerate(p['lines']):
            tasks.append(gen(de, f"{OUT_DIR}/p{i}_{j}.mp3"))
    for i, t in enumerate(data['twisters']):
        tasks.append(gen(t, f"{OUT_DIR}/tt{i}.mp3"))
    for i, pr in enumerate(data['prompts']):
        tasks.append(gen(pr, f"{OUT_DIR}/fp{i}.mp3"))
    tasks.append(gen(data['test_phrase'], f"{OUT_DIR}/test.mp3"))

    # Limit concurrency to be a reasonable citizen toward the service.
    sem = asyncio.Semaphore(6)
    async def bound(t):
        async with sem:
            return await t
    results = await asyncio.gather(*[bound(t) for t in tasks], return_exceptions=True)
    errors = [r for r in results if isinstance(r, Exception)]
    print(f"Done. {len(tasks)} clips requested, {len(errors)} errors.")
    for e in errors[:10]:
        print("ERROR:", repr(e))

asyncio.run(main())
