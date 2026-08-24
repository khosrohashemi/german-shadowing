import asyncio, json, os
import edge_tts
from mutagen.mp3 import MP3

VOICE = "de-DE-KatjaNeural"
OUT_DIR = "audio"

async def gen(text, path):
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save(path)

async def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    with open('podcast_content.json', encoding='utf-8') as f:
        episodes = json.load(f)

    tasks = []
    for ep in episodes:
        script = ep['script'].replace('\n\n', ' ... ').replace('\n', ' ')
        tasks.append(gen(script, f"{OUT_DIR}/{ep['id']}_full.mp3"))
        for qi, q in enumerate(ep['questions']):
            tasks.append(gen(q['q'], f"{OUT_DIR}/{ep['id']}_q{qi}.mp3"))

    sem = asyncio.Semaphore(6)
    async def bound(t):
        async with sem:
            return await t
    results = await asyncio.gather(*[bound(t) for t in tasks], return_exceptions=True)
    errors = [r for r in results if isinstance(r, Exception)]
    print(f"Done. {len(tasks)} clips requested, {len(errors)} errors.")
    for e in errors[:10]:
        print("ERROR:", repr(e))

    for ep in episodes:
        path = f"{OUT_DIR}/{ep['id']}_full.mp3"
        dur = MP3(path).info.length
        print(f"{ep['id']} ({ep['title']}): {dur:.1f}s = {dur/60:.2f} min")

asyncio.run(main())
