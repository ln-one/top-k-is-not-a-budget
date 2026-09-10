# 实验初稿证据映射（v2）

本轮真实结果统一位于 `results/paper-experiments-v2/`。初稿并非提交前的独立复现完成声明。

- 设置与覆盖：manifest.json、input-audit.json、verification.json。
- 固定L迁移：transfer-grid.csv、transfer-calibration.csv、transfer-test.csv、transfer-summary.csv。选择标准为线性nDCG10，校准和留出分离。
- 固定K成本与认证位置：fixed-k.csv、cost-summary.csv、trajectory-events.csv、certificate-gaps.csv。未观测完成成本保留下界。
- 预算产出与粒度：aggregate.csv、paired.csv、auc-aggregate.csv。nAUC存在观测区间，不能把下界写成精确值。
- 质量成本：quality-cost-grid.csv、quality-budget-calibration.csv、quality-budget-heldout.csv、quality-budget-summary.csv。95%是校准目标，留出比例为均值之比；全查询节省下界与完成子集精确节省分列。
- 数值核验：独立认证器核对12961状态；外部评测器核对29440行nDCG20，误差小于1e-12。
- 图：figures/paper-v2，真实CSV输入，观测区间与bootstrap区间分别标明。

限制：五个静态集合已有探索历史；时间快照不是独立查询。排序回放成本不是在线时延。旧Pressure与截断质量结果保留，不主张新SNRA或相关性优于截断。
