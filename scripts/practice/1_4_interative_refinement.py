# -*- encoding: utf-8 -*-
"""
@File    : iterative_refinement.py
@Time    : 2026/6/19 15:30
@Desc    : 逐步调试prompt, 观察哪些会提升质量。
"""
import os
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

prompts = {
    "v1 模糊": "写一段介紹 ReAct 的文字。",
    "v2 加目标读者": "写一段介紹 ReAct 的文字、给写过 Python 的软体工程师看。",
    "v3 加格式": "写一段介紹 ReAct 的文字、给写过 Python 的软体工程师看。100 字以內、用一个段落。",
    "v4 加 example 要求": "写一段介紹 ReAct 的文字、给写过 Python 的软体工程师看。100 字以內、用一个段落、结尾举一个具体例子（譬如查天气）。",
    "v5 加禁忌": "写一段介紹 ReAct 的文字、给写过 Python 的软体工程师看。100 字以內、用一个段落、结尾举一个具体例子（譬如查天气）。不要用「赋能」「驱动」「智能」这类空泛词语。",
}

outputs = {}
for label, prompt in prompts.items():
    response = client.chat.completions.create(
        model="ernie-x1-turbo-32k",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    text = response.choices[0].message.content.strip()
    outputs[label] = text
    print(f"\n--- [{label}] ({len(text)} chars) ---")
    print(text)

banned_words = ("赋能", "驱动", "智能")
v5_has_banned = any(w in outputs["v5 加禁忌"] for w in banned_words)
print(f"\nv5 是否包含禁忌词: {'是' if v5_has_banned else '否'}, v4 是否包含禁忌词: {'是' if any(w in outputs['v4 加 example 要求'] for w in banned_words) else '否'}")






