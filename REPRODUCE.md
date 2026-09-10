# 复现当前论文实验

## 范围

已有五查询集静态回放（770查询）和五时间快照回放（同30查询、150查询—快照组合）。重算认证、补零输出、逐查询质量和宏平均。静态调度轨迹来自已发布的冻结CSV；本入口重算轨迹端点的认证与融合，不从头生成静态检索排名或重新执行静态调度。时间实验从冻结通道排名重新执行调度。不调用检索引擎，不测时延。

## 输入与环境

输入包 `replay-inputs.tar.gz` 在本机 `data/` 下（Git忽略），含静态与时间实验的rank前缀、完整融合Top101参考、qrels和run元数据。未上传GitHub；其他机器需要获得此包或等价的canonical-v1目录。源清单保留SHA-256，执行前逐文件校验。不是只克隆仓库就具备全部数据。

验证环境为CPython3.12.13、macOS arm64。只用固定版本的NumPy、SciPy和pytrec-eval-terrier；其他平台尚未验证。

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-replay.txt
mkdir -p data/inputs
tar -xzf data/replay-inputs.tar.gz -C data/inputs
.venv/bin/python scripts/reproduce_paper.py --data-root data/inputs
```

默认输出 `tmp/reproduction/`，避免覆盖已发布结果。`--output` 可另指定目录。各阶段单独脚本均支持 `--help`。

## 结果和口径

- 原始静态对照：`results/matched-budget-truncation/`。
- 外部评测复核：`results/metric-audit/`，分别导出线性和指数增益nDCG。
- 时间轨迹及源清单：`results/temporal-prefix/`。
- 时间预算对照：`results/temporal-matched/`。
- 时间外部评测：`results/temporal-metric-audit/`。
- 可读结论：`results/validation-summary.md`。

历史nDCG使用2^rel−1增益；trec_eval默认用rel线性增益。两者不能混列为同一个指标。外部工具对指数增益使用转换后的qrels，Recall仍以原始rel>0为相关。TREC-DL若采用不同二值相关阈值需另报，当前并不声称逐项复现所有TREC官方任务口径。静态TREC-COVID有两条−1标注，外部评测按零增益处理，本轮没有影响任何已报nDCG结果。

RRF固定历史offset59，即1/(59+r)，不是标准offset60。逐通道排名为精确前缀，读取预算为条目数，不能解释为ANN在线成本或p95时延。保存排名到末端不代表源真正耗尽。评估上限20/100不等同于输入K目标。

时间实验复用同30查询及已有EAHR快照，非150条独立查询、也非全新未触碰测试集。跨快照qrels亦变化，不能把跨轮nDCG差异全归因于语料更新。相同快照内的配对方法比较才有一致标注基础。

## 重新打包数据

```bash
.venv/bin/python scripts/package_replay_inputs.py --data-root /path/to/canonical-v1 --output data/replay-inputs.tar.gz
```

## 尚不包含

此复现包不从原始语料重新编码Dense向量或重建Sparse索引；那一层仍需要EAHR源系统及模型/数据构建配置。只读已有CSV可核查汇总，取得输入包后可复现融合回放。
