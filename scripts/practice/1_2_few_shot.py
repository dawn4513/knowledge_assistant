# -*- encoding: utf-8 -*-
"""
@File    : few_shot.py
@Time    : 2026/6/19 7:30
@Desc    : few shot 调试, 在 prompt 中给模型提供 1-2 个示例，测试对模型输出的影响
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

TEST_SET = [
    ("这部电影超赞、看完想再看一次！", "正面"),
    ("剧情无聊、演员演技尴尬。", "负面"),
    ("这是一部 2019 年的电影。", "中立"),
    ("我不确定喜不喜欢、可能再想想。", "中立"),
    ("第一集很不错但第二集就崩了。", "负面"),
    ("看完心情很好、推荐！", "正面"),
]

FEW_SHOT_EXAMPLES = """范例：
input: 这家餐厅的牛排好吃到让我哭出来。
output: 正面

input: 服务生态度很差、我再也不会来了。
output: 负面

input: 这家店位于新北市三重区。
output: 中立
"""

def classify(text, use_few_shot=False):
    prefix = FEW_SHOT_EXAMPLES + "\n" if use_few_shot else ""
    prompt = f"{prefix}input: {text}\noutput:"

    response = client.chat.completions.create(
        model="ernie-x1-turbo-32k",
        messages=[
            {"role": "system", "content": "你是一个情感分析专家，判断用户评论的情感倾向是正面、负面还是中立。"},
            {"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()


def evaluate(use_few_shot=False):
    correct = 0
    for text, label in TEST_SET:
        pred = classify(text, use_few_shot)
        print(f"input: {text}\npred: {pred}, label: {label}\n")
        if pred == label:
            correct += 1
    return correct, len(TEST_SET)

print("=== zero-shot ===")
correct, total = evaluate(use_few_shot=False)
print(f"Correct: {correct}, Total: {total}")

print("=== few-shot ===")
correct, total = evaluate(use_few_shot=True)
print(f"Correct: {correct}, Total: {total}")
