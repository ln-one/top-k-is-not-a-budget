# Budgeted Exact Prefix

从 EAHR 的 Top-K 毒丸现象出发，研究给定读取预算下的精确混合检索结果输出。此仓库是供合作者接手的独立候选项目，目标是围绕现有方法完成验证和论文；ICASSP 是考虑中的投稿目标，尚未定稿。

## 接手先看

1. [交接说明](HANDOFF.md)：范围、已有证据和下一步。
2. [候选方案](plan/research/budgeted-prefix-candidate-zh.md)：方法及其边界。
3. [毒丸案例](results/poison-case-analysis.md)与[五集合分析](results/poison-generalization-five-datasets.md)。
4. [五集合调度对比](results/anytime-five-datasets-chunk64/analysis.md)与[质量—预算结果](results/quality-budget-frontier-five-datasets.md)。
5. [相关工作](plan/research/prior-art-map.md)：明确 SNRA、LARA-IN 等前人基础。

## 方法

Dense/Sparse 流提供精确排名前缀；WRRF 上下界认证当前可交付的有序前缀，blocker 规则选择下一条推进的通道。预算耗尽后返回已认证部分，K 为输出长度。讨论简称“SNRA 式调度 + LARA-IN 式增量输出”，不表示原算法的完整组合实现，也不声称这些基础思想原创。

当前实验预算为逻辑读取量，不是时间；精确性针对完整 WRRF 排序的前缀，不表示召回已足够，也不保证每个查询都避免毒丸开销。

## 直接复查已有数据

以下分析只需要 Python 3 标准库，无须原始数据或模型。命令在仓库根目录执行：

```sh
mkdir -p tmp
python3 scripts/analyze_quality_budget_frontier.py \
  --frontier results/anytime-five-datasets-chunk64/derived/anytime_frontier_per_query.csv \
  --output tmp/quality-budget.md
python3 scripts/analyze_interruptible_contract.py \
  --frontier results/anytime-five-datasets-chunk16/derived/anytime_frontier_per_query.csv \
  --output tmp/interruptible-contract.md
```

上面两条命令分别使用 chunk64 和 chunk16，与对应历史报告一致；交接时已验证生成内容与两份报告逐字节一致。这只重新汇总现有 CSV，不是重跑检索，也不是独立验证全部结果的精确性。

## 完整回放

主要入口为 `scripts/run_anytime_frontier_pilot.py`。所需 Python 包列于 `requirements.txt`，该列表不是原实验环境的版本锁定。原始冻结排名、qrels、完整 EAHR 系统及大型模型/索引未打包；因此新机器克隆后不能直接重跑完整回放。

准备原始数据后显式传入 `--source-root`，不要使用脚本中保留的作者机器默认路径。所需布局为：

```text
canonical-v1/
  experiments/target-validity/static-v3/<dataset>/run.json
  experiments/target-validity/static-v3/<dataset>/queries/...
  datasets/<dataset>/source/qrels.tsv
```

```sh
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 scripts/run_anytime_frontier_pilot.py \
  --source-root /path/to/canonical-v1/experiments/target-validity/static-v3 \
  --output-root tmp/replay --chunk 64 --oracle-grid 64 --include-candidate \
  --datasets msmarco-passage-trec-dl-2019 msmarco-passage-trec-dl-2020 trec-covid scifact nfcorpus
```

历史验证脚本和部分分析脚本也保留了原始绝对路径，需要按原始 manifest 恢复数据或做路径迁移。旧绘图脚本可能依赖平台工具。原始来源及哈希见各 `results/**/raw/*manifest.json`。

## 来源与范围

从 `adaptive-top-k` 选取代码和实验快照，未复制原 Git 历史。文件来源、原提交及 SHA-256 见 [HANDOFF-MANIFEST.json](HANDOFF-MANIFEST.json)。当前候选记录是交接时额外纳入的未提交文档。

`plan/` 中保留历史讨论，部分结论已被后续讨论调整，部分链接指向未打包的父项目或物理索引分支。当前范围以本 README 和 HANDOFF.md 为准。PAVE/LPAVE 等索引实现与大型产物未纳入本项目。

## 2026-09-10 论文工作版本

已确认中文稿件位于 [paper/icassp2027](paper/icassp2027/README.md)。当前复现入口见 [REPRODUCE.md](REPRODUCE.md)，包括外部指标审计和新增五轮时间验证。历史HANDOFF仅作背景；本轮不要求内核或真实时延实验。输入数据包本地单独保存，未上传。
