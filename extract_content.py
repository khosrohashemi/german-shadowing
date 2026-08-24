import re, json

with open('index.html', encoding='utf-8') as f:
    content = f.read()

def extract_block(varname, content):
    start = content.index('const ' + varname + ' = [')
    i = content.index('[', start)
    depth = 0
    j = i
    while True:
        if content[j] == '[':
            depth += 1
        elif content[j] == ']':
            depth -= 1
            if depth == 0:
                break
        j += 1
    return content[i:j+1]

STR = r'"((?:[^"\\]|\\.)*)"'

passages_block = extract_block('PASSAGES', content)
passage_entries = re.findall(r"\{c:'(\w+)', level:'(\w+)', lines:\[(.*?)\]\}", passages_block, re.S)
passages = []
for c, level, lines_block in passage_entries:
    lines = re.findall(r'\{de:' + STR + r', en:' + STR + r'\}', lines_block)
    assert len(lines) == 3, lines_block
    passages.append({'c': c, 'level': level, 'lines': lines})
print("passages:", len(passages))

tt_block = extract_block('TONGUE_TWISTERS', content)
twisters = re.findall(STR, tt_block)
print("twisters:", len(twisters))

fp_block = extract_block('FREESTYLE_PROMPTS', content)
prompts = re.findall(STR, fp_block)
print("freestyle prompts:", len(prompts))

data = {
    'passages': passages,
    'twisters': twisters,
    'prompts': prompts,
    'test_phrase': 'Hallo! Kannst du mich hören? Das ist ein Test.'
}
with open('tts_content.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=1)
print("wrote tts_content.json")
