# 实验v2复现与初稿

本轮完成三组八项分析及精确Top20质量—成本校准对照。旧结果未删除。输入来自既有冻结排名，不重新生成检索输入。

## 命令

在仓库根目录，以当前 `.venv` 或按 `requirements-paper-v2.txt` 安装的Python3.12环境执行：

```bash
python scripts/run_paper_experiments_v2.py --smoke --output results/paper-experiments-v2-smoke-new
python scripts/run_paper_experiments_v2.py --output results/paper-experiments-v2-new
```

汇总、校验和绘图脚本当前读取 canonical 目录 `results/paper-experiments-v2/`。重跑时先保留原目录，再将新目录作为 canonical 输入；不要覆盖原实测证据。脚本：

```bash
python scripts/analyze_paper_experiments_v2.py
python scripts/verify_paper_experiments_v2.py
python figures/paper-v2/plot_results.py
python scripts/build_paper_experiments_tables.py
make -C paper/icassp2027/latex
```

数据包位置与校验见根目录 REPRODUCE.md。结果输入不是仅克隆即可获得。数组认证器与grouped维护器的逐步smoke比较共296562次；全部预算输出另有外部评测与数组端点验证。

## 核心结果

- 全量920查询条件×两策略×两粒度，共3680条轨迹、29440预算记录。
- B2048，静态五集合等权平均cap100由41.771958增至45.054587，+7.85845%；cap20由18.070547增至18.178779。
- 95%校准目标下，NFCorpus留出质量95.8059%，访问减少65.9202%；SciFact质量97.6763%，访问减少83.4126%。
- 两个TREC-DL和COVID的部分完整Top20成本未观测，因此全体成本节省为保守下界，不是精确成本测量。详见quality-budget-summary.csv。
- 部分高预算产出有观测区间；旧脚本将末端后的保留前缀当作端点值，本轮明确改为上下界。不能将两种口径混列。
- 未通过99%校准的折保留，固定L优于完整RRF的相关性结果保留。

中文实验初稿与完整英文PDF已更新。PDF是未经篇幅压缩的工作稿，不是已满足投稿页数要求的终稿。
