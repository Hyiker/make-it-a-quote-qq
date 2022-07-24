# coding:utf-8
from dataclasses import dataclass
import re


@dataclass
class Question:
    question: str
    answer: str
    options: list[str]
    analysis: str = ''


def read_questions(filename: str):
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    questions = []
    # question, options, answer
    i = 0
    while i < len(lines):
        description = ''
        answer = ''
        options = []
        analysis = ''
        q = []
        first = True
        while i < len(lines):
            line = lines[i].strip()
            if not line or len(line) == 0:
                i += 1
                continue
            # end with line start with \d\.
            if re.match(r'^\d+\.', line):
                if first:
                    first = False
                else:
                    i -= 1
                    break
            q.append(line)
            i += 1
        # find line start with 答案：
        j = 0
        while j < len(q):
            line = q[j]
            if line.startswith('答案：'):
                break
            j += 1
        # find line start with alphabetical word
        k = 0
        while k < len(q):
            line = q[k]
            if re.match(r'^[a-zA-Z]+\.', line):
                break
            k += 1
        answer = q[j].replace('答案：', '').strip().lower()
        description = '\n'.join(q[0: k])
        options = q[k: j]
        if j < len(q):
            analysis = '\n'.join(q[j + 1:])
        questions.append(Question(description, answer, options, analysis))
        i += 1

    return questions


if __name__ == '__main__':
    q = read_questions('questions.txt')
    print(q)
