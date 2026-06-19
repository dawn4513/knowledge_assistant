# -*- encoding: utf-8 -*-
"""
@File    : CoT.py
@Time    : 2026/6/19 15:11
@Desc    : Chain of Thought 调试, 在 prompt 中给模型提供思考过程，测试对模型输出的影响。
            对 reasoning-native 模型，用它们的 extended thinking 通常比你手写“Let's think step by step”更好；硬塞步骤反而可能干扰它本来的推理。手写 CoT 仍适用于不具内置推理的一般 chat model。
"""
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")

url = "https://qianfan.baidubce.com/v2"
api_key = os.environ.get("QIANFAN_API_KEY")
if not api_key:
    raise RuntimeError("请在项目根目录的 .env 文件中设置 QIANFAN_API_KEY")

client = OpenAI(
    api_key=api_key,
    base_url=url
)

QUESTION = "小明有 3 颗苹果。他给了小華 1 颗、又从媽媽那边拿到 5 颗、然后吃了 2 颗，又从爸爸那边拿到 1 颗。请问现在剩几颗？"
ANSWER = 6  # 3 - 1 + 5 - 2 + 1 = 6


COT_EXAMPLE = """范例：
Q: 一只鸡有 2 只脚。3 只鸡跟 1 个人共有几只脚？
A: 让我一步一步算。3 只鸡 × 2 只脚 = 6 只脚。1 个人有 2 只脚。總共 6 + 2 = 8 只脚。答案是 8。
"""


def ask(text):
    response = client.chat.completions.create(
        model="ernie-x1-turbo-32k",
        max_tokens=300,
        messages=[
            {"role": "user", "content": text}]
    )
    return response.choices[0].message.content.strip()


def extract_number(text: str):
    nums = re.findall(r"-?\d+", text)
    return int(nums[-1]) if nums else None


# A. 纯 prompt
out_a = ask(QUESTION); ans_a = extract_number(out_a)

# B. + Let's think step by step
out_b = ask(QUESTION + "\n让我一步一步算."); ans_b = extract_number(out_b)

# C. + CoT example
out_c = ask(COT_EXAMPLE + "\n\nQ: " + QUESTION + "\nA:"); ans_c = extract_number(out_c)

for label, out, ans in [("A 纯 prompt", out_a, ans_a), ("B +step-by-step", out_b, ans_b), ("C +CoT example", out_c, ans_c)]:
    print(f"\n--- [{label}] 答案={ans} {'✓' if ans == ANSWER else '✗'} ---")
    print(out[:200])
