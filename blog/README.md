# 通用人工智能（AGI）科普系列

<div align="center">
<img src="../images/sparrow.png" width="160">

**用通俗的语言、图文并茂地讲清楚：通用人工智能的过去、现在与未来**

</div>

---

## 📚 系列目录

| 篇目 | 标题 | 你将了解 |
|---|---|---|
| 第一篇 | [什么是通用人工智能？](01-what-is-agi.md) | AGI 与专用 AI 的区别、AGI 应具备的能力、怎样判断是否实现了 AGI |
| 第二篇 | [七十年风雨路——AGI 的发展历史](02-history.md) | 从图灵测试到 ChatGPT：三次高潮、两次寒冬，以及每个阶段的经验教训 |
| 第三篇 | [大模型时代——AGI 的现状](03-present.md) | 2023—2026 年的重要进展、大模型的工作原理、今天的 AI 离 AGI 还有多远 |
| 第四篇 | [AGI 的未来——路线、挑战与希望](04-future.md) | 通往 AGI 的六条技术路线、可能带来的机遇与风险、普通人如何应对 |

<p align="center">
  <img src="../images/blog/02-ai-timeline.svg" alt="人工智能发展时间线" width="100%">
</p>

---

## 🔤 术语小词典

| 术语 | 通俗解释 |
|---|---|
| **AI（人工智能）** | 让机器表现出智能行为的技术总称 |
| **AGI（通用人工智能）** | 能像人一样学习并完成各种智力任务的 AI |
| **ASI（超级人工智能）** | 在几乎所有方面都远超人类的假想中的 AI |
| **神经网络** | 模仿大脑神经元连接方式的计算模型，由大量可调的“参数”组成 |
| **深度学习** | 使用很多层神经网络、从大量数据中自动学习的方法 |
| **Transformer** | 2017 年提出的神经网络架构，靠“注意力机制”理解上下文，是当今大模型的基础 |
| **大语言模型（LLM）** | 在海量文本上训练、能理解和生成语言的超大神经网络，如 GPT、Claude、DeepSeek、通义千问等 |
| **参数** | 神经网络中可以调整的数值，可以理解为“旋钮”；参数越多，模型容量越大 |
| **预训练 / 微调** | 先在海量通用数据上“打基础”，再用特定数据“学专业” |
| **RLHF** | 基于人类反馈的强化学习：让人给 AI 的回答打分，AI 据此改进 |
| **规模定律** | 模型越大、数据越多、算力越强，性能就可预测地越好 |
| **涌现** | 模型规模达到一定程度后，突然出现小模型没有的能力 |
| **幻觉** | AI 一本正经地生成错误或编造的信息 |
| **多模态** | 能同时处理文字、图像、声音、视频等多种信息 |
| **推理模型** | 在回答前先进行较长“思考”的模型，擅长数学、编程等复杂问题 |
| **智能体（Agent）** | 能自主规划、使用工具、多步行动来完成任务的 AI |
| **世界模型** | AI 对“世界如何运转”的内部模拟，用来预测行动的后果 |
| **具身智能** | 拥有身体（如机器人）、能在物理世界中感知和行动的 AI |
| **对齐（Alignment）** | 让 AI 的目标和行为符合人类意图与价值观 |
| **知识蒸馏** | 让大模型把本领“教”给小模型，使小模型又小又强 |

---

## 📖 延伸阅读

- 艾伦·图灵，《计算机器与智能》（*Computing Machinery and Intelligence*），1950
- Vaswani 等，《Attention Is All You Need》，2017
- Kaplan 等，《Scaling Laws for Neural Language Models》，2020
- Morris 等，《Levels of AGI for Operationalizing Progress on the Path to AGI》，2023
- 斯图尔特·罗素、彼得·诺维格，《人工智能：一种现代方法》
- 梅拉妮·米歇尔，《AI 3.0》（*Artificial Intelligence: A Guide for Thinking Humans*）

---

## ✍️ 关于本系列

本系列由 [SMART 项目](../profile/README_CN.md) 社区编写，内容截至 2026 年 9 月。AI 领域发展迅速，如发现错误或过时的内容，欢迎提交 Issue 或 Pull Request 帮助改进。

文中配图位于 [`images/blog/`](../images/blog/)，由脚本 [`generate_figures.py`](../images/blog/generate_figures.py) 生成，修改脚本后重新运行即可更新全部图片：

```bash
python3 images/blog/generate_figures.py
```
