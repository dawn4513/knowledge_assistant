# -*- encoding: utf-8 -*-
"""
@File    : system_prompt.py
@Time    : 2026/6/19 7:00
@Desc    : prompt 调试, system prompt + user prompt, 测试不同的 system prompt 对模型输出的影响
"""
import time
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

SYSTEM_PROMPTS = {
    "严肃律师": "你是严谨的合约律师。回答要精准、引用法条编号、避免任何主观形容词。",
    "幼儿园老师": "你是温柔的幼儿园老师、要对 5 岁小孩说话。用比喻、口语、少于 80 字。",
    "JSON 机器": "你只回 JSON。schema: {\"answer\": string, \"confidence\": float}",
}

USER_MSG = "请帮我解释什么是租赁合约。"

for label, prompt in SYSTEM_PROMPTS.items():
    t0 = time.time()
    response = client.chat.completions.create(
        model="ernie-x1-turbo-32k",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": USER_MSG}
        ]
    )

    text = response.choices[0].message.content
    print(f"({label}, 回应：{text}, latency={time.time() - t0:.2f} sec)")
    print("usage:", response.usage)

# assert response.choices[0].finish_reason in ["stop", "length"], f"unexpected finish reason: {response.choices[0].finish_reason}"
# assert text is not None, "response text is None"
# assert len(text) > 0, "response text is empty"
