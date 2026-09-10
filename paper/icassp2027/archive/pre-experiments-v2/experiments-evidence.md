# 实验稿证据映射（非正文）

2026-09-10 中文实验初稿。遵循用户决定：正文不纳入截断质量比较，既有结果不删除。无新实验或显著性声明。

| 正文主张 | 证据 | 口径 |
|---|---|---|
| 五集合认证曲线提升1.06%–5.95% | results/anytime-five-datasets-chunk64/derived/anytime_frontier_per_query.csv；scripts/analyze_anytime_replays.py | 逐查询log预算梯形积分，归一化跨度和cap100；本轮从CSV重新计算确认 |
| 预算2048，cap100为41.77→44.87、cap20为18.07→18.17 | results/matched-budget-truncation/macro.csv | 仅取balanced_cert/blocker_cert，五集合等权 |
| 五轮同30查询平均认证产出 | results/temporal-matched/aggregate.csv | budget2048、cap20；主文展示点，全部八预算留在仓库 |
| 所有已认证前缀逐位正确 | results/matched-budget-truncation/manifest.json；results/temporal-matched/manifest.json | 静态12320和时间2400个balanced/blocker认证状态重现和完整参考检查 |
| 检索器配置 | EAHR paper/chapters/03_Experimental_Setting_zh.md及冻结run元数据 | bge-small-en-v1.5, BM25 k1=.9,b=.4；正式引文后补 |

限制：单Dense/Sparse组合、精确源排名、逻辑读取、既有查询重复评估；不推断RAG生成质量、时延优势、全局最优或独立方法新颖性。竞争压力在四位小数下与本文方法接近，不能声称本文全面胜过所有强基线。输入cap100仅报告用途。
