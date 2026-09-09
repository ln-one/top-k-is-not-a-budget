# 自适应 Top-K / 无 K 精确混合检索：综合研究结论

## 一句话结论

你的现象判断是对的，接口判断也基本对：固定 Top-K 越大，精确 WRRF
证书的“毒丸”比例会急剧上升；让 Dense 和 Sparse 在同一预算下不对称推进，
确实比 50/50 更合理。但把它写成“无 K + 固定总 depth + first-blocker”并不够
成为一篇稳 CCF-B 的新论文，因为无 K 精确枚举和 first-blocker 的算法核心都
有经典先例，而且当前 Dense 后端在第一次输出前仍会扫描整个向量库。

这项研究真正得到的不是一个待包装的方法，而是一个较清楚的 go/no-go：

- 中间的 rank 调度层已经被先验工作和实验上限同时挤压；
- 要继续成篇，必须向下发明真正可中断的物理精确索引，或向上改成另一个有
  校准数据和任务效用的语义风险问题；
- 目前最诚实的决定是暂停这篇，而不是把一个有用 API 勉强写成算法论文。

## 1. 原始直觉哪些被证实了

### 1.1 Top-K 越大，毒丸确实快速增多

五个 query set、770 个查询的离线精确 replay 显示，在每个通道最多读取
5,000 条的审计窗口内，无法证明 ordered Top-K 的 equal-dataset macro 比例为：

| K | 5 | 10 | 20 | 50 | 100 |
|---:|---:|---:|---:|---:|---:|
| ordered 证书失败 | 0.00% | 2.13% | 13.48% | 36.28% | 51.31% |

TREC-COVID 在 K=20 已达到 34%，K=50 达到 72%；TREC-DL 2020 在 K=100
达到 94.44%。这不是两个个例。

机制也符合你的直觉：K 增大后，边界分数下降，更多只在一个通道靠前的候选
进入竞争；它在另一通道尚未出现时仍保留一项可能的 WRRF 增益，于是内部次序
或集合边界迟迟不能确定。

### 1.2 Dense 和 Sparse 不应该被迫对称

在 97 个 TREC-DL 查询、8 个总工作预算上，SNRA/first-blocker 式调度在
全部 776 个状态上匹配了步长 16 的 allocation-grid envelope；在总工作
2,048 时，87.6% 的查询使用了不等深度，Dense 占比从 19.5% 到 89.1%。

扩展到五个 query set 后，first-blocker 相对 50/50 balanced 的 nAUC-cert
提升在每个集合上都为正，约 1.07%--5.94%。因此“不对称推进”是真实现象，
不是两个毒丸制造的错觉。

### 1.3 固定总 depth 是比固定 K 更自然的实验控制

它把两个问题分开了：

1. 当前已经证明了多少个完整 WRRF 前缀；
2. 调用方愿意继续花多少资源。

在总逻辑工作 128 时，五集合等权平均已经返回 12.35 个精确结果，nDCG@10
保留 86.35%，但 Recall@100 只保留 42.74%。到工作 2,048，二者分别为
99.07% 和 70.46%。这说明连续精确前缀对头部质量很有用，但它不能自己判断
“语义证据已经够了”。

所以固定 depth 是合理的工程/实验参数；问题只是它不是新的学术贡献。

## 2. 两类毒丸其实不同

把严格顺序证书换成只要求 Top-K 身份集合后，macro 失败率明显下降：

| K | 5 | 10 | 20 | 50 | 100 |
|---:|---:|---:|---:|---:|---:|
| ordered | 0.00% | 2.13% | 13.48% | 36.28% | 51.31% |
| set-only | 0.00% | 0.40% | 4.61% | 23.37% | 34.94% |

因此 K=20 的 13.48% 中，8.88 个百分点只是“集合已经知道，但内部顺序仍有
歧义”，真正的 membership poison 是 4.61%。两个原始毒丸在其问题 K 上也
属于 set-safe。

这对 EAHR 的产品接口很有价值：如果下游把文档当集合使用，可以不用为无关的
内部交换继续检索。但 set-safe 本身是成熟的 top-k 语义，而且仍然需要调用方
给 K，所以它更适合作为 EAHR 扩展，不足以单篇承载创新。

## 3. 为什么“边检索边决定 K”仍然需要一个外部参数

最干净的精确接口确实是：

```text
start(query)
while budget/deadline remains:
    advance one Dense or Sparse action
    expose longest certified prefix
return the last certified prefix
```

K 在这里是输出，不是输入。但系统仍必须知道什么时候返回：deadline、CPU/I/O
预算、token 预算、风险容忍度或某个任务效用阈值至少要有一个。完全没有任何
外部偏好的有限停止机制并不存在于这个 exactness 目标中，因为下一个未读贡献
始终可能改变下一名；而“已经精确”也不等于“已经足够回答问题”。

因此最优雅的表达不是“parameter-free stopping”，而是：

> 检索器参数无 K，持续给出最长精确前缀；资源或语义停止属于调用方合同。

## 4. 为什么算法层不够新

最致命的近邻不是近两年 RAG，而是经典数据库算法：

- J*（VLDB 2001）已经按需拉取 ranked inputs，并逐个输出下一条精确答案；
- LARA-IN（ICDE 2006/TODS 2007）明确写出 `without a constraint k`，提供
  stateful `GetNext()` 的 sorted-access-only 精确聚合；
- Selective NRA / SNRA（2009/2012）推进当前最大上界竞争者所缺失的来源，
  这正是 first-blocker 的原则；
- Upper、IO-Top-k、CARS、Best-Effort Top-k 和 contract scheduling 已覆盖
  异构成本、预算调度和未知中断的相邻问题。

WRRF 是各列表递减 reciprocal-rank 贡献的单调和，所以不能靠“它是混合检索”
逃离这些聚合模型。

实验也没有留下足够的算法空间：在 Dense:Sparse 成本比从 1:16 到 16:1 的
18 个 TREC 条件中，步长 8 的离线分配 envelope 只比最强可部署规则高
0.58%--2.00% relative nAUC。HSNRA、doubling hedge、boundary-pressure 和从
小规模 minimax 游戏导出的 candidate-safe 规则都没有在真实 replay 上超过
SNRA。继续造 rank-only heuristic 很难形成可信论文。

## 5. 更关键的问题：逻辑 depth 不等于物理计算

当前 PVS 是很强的 exact refinement certificate，却不是物理可渐进 Dense
source。代码在构造 cursor 时先对所有 eligible vectors 计算 int8 区间，再把
区间放进 heap，之后 fusion 才能开始请求 rank。

冻结的 8,841,823 文档 MS MARCO E5 pilot 给出了直接证据：

- 8 个查询、每个 4 次正式测量，fused top-20 零 membership/order mismatch；
- 每一次 PVS 都评估全部 8,841,823 个 int8 行；
- f32 精确 refinement 中位比例只有 0.05112%；
- PVS 相对 f32 scan 的 paired median speedup 是 16.86x，8 个查询中 7 个更快；
- 但一个难查询需要约 104,656 次 Dense 逻辑拉取和 329,184 次 refinement，
  PVS 中位耗时 31.46 s，反而只有 scan 的 0.58x。

也就是说，PVS 通常通过“把全精度扫描换成便宜的全库 int8 扫描”获胜，而不是
通过“只读取几百个 rank”跳过大部分库。逻辑调度再漂亮，也消不掉这个启动成本。

## 6. 为什么最自然的物理方案也暂时不通

要在第一次结果前避免全库 per-vector bound，必须有一个安全的聚合上界：一次
计算某个 block/tree node 的上界，就能排除整个区域。否则任何尚未检查的向量
都可能高于当前候选，精确 top-1 不能发出。

我们已经有真实负结果，不需要重新做最简单的球树：

- SciFact 5,183 文档、384 维、100 查询；
- HNSW proposal 的 top-20 完全正确；
- 随后的 hierarchical Euclidean + spherical-cap certificate 仍计算
  518,300/518,300 个可能的精确分数；
- combined p50 1.750 ms，而 exact scan 只有 0.181 ms；
- 叶大小压到 2 时也只跳过约 7.5% exact scores，同时仍评估所有 node bounds。

高维界太松正是难点。若要继续，必须比 center-radius tree 明显更强，并直接面对
branch-and-bound MIPS、LEMP、MAXIMUS/OPTIMUS 等 exact-MIPS 先验工作。

## 7. 改成近似或语义停止也不是低成本逃生路线

近似物理增量已有 EI-LSH、SIGIR 2025 IGP；Sparse 的概率 rank-safeness 有
EMNLP 2024 ASC。语义 K 和 RAG 停止已有 Where to Stop、Choppy、AttnCut、
Adaptive-k、FLARE、Adaptive-RAG、DRAGIN、Stop-RAG、AutoSearch 等。

统计保证也已形成直接邻域：Two-stage Risk Control for Ranked Retrieval、
conformal context filtering、multi-turn conformal stopping、Know Before You Fetch、
AB-RAG。若转向这里，需要新的 query-disjoint calibration、reader outputs、token/
latency costs、多模型多任务和相应强基线；它会是一篇新项目，不是当前 replay 的
最后一块拼图。

## 8. 最终 paper decision

| 路线 | 决定 |
|---|---|
| 固定总逻辑 depth + first-blocker | **Red：不单篇** |
| set-safe EAHR | **Amber/red：适合扩展或技术说明** |
| 当前 PVS/PBM 上加 deadline API | **Red：工程价值，不是论文原语** |
| 把 PVS 单拆一篇 | **Red：已是 EAHR 核心，除非有大幅新结果** |
| 新的 aggregate-index exact Dense + Sparse 物理调度 | **Amber/red：唯一高上限系统路线，但工作量大、先验重** |
| 近似增量 + calibrated risk | **Amber：可能成篇，但属于另一个项目** |
| 自主语义停止 RAG | **Amber/red：拥挤且缺当前所需数据** |

若物理精确索引真的在多个真实向量库上跳过 20%--30% 以上工作，并改善
time-to-first 和 area-under-time-to-certified-prefix，同时打过 PVS、scan 和
exact-MIPS 基线，才值得按稳 B 冲 A 的标准重新启动。否则转向下一题更合理。

## 9. 可复查产物

- 总体先验图：`plan/research/prior-art-map.md`
- WRRF 到 LARA 的形式映射：`plan/research/wrrf-lara-reduction.md`
- 停止合同：`plan/research/stopping-contracts.md`
- 五集合毒丸：`results/poison-generalization-five-datasets.md`
- 质量--预算曲线：`results/quality-budget-frontier-five-datasets.md`
- ordered/set 分解：`results/set-certificate-five-datasets.md`
- 物理 first-output 条件：`plan/research/physical-first-output-bound.md`
- 8.84M 物理审计：`results/msmarco-8m-physical-cost-audit.md`
- 备选论文路线：`plan/research/alternative-paper-portfolio.md`

所有当前已声称的 replay prefix 都经过 frozen complete-list oracle 核验；逻辑
depth 结果没有被写成 latency 结果。8.84M 报告由只读脚本从冻结 JSONL 重建，
排除了 warmup 和独立 validation latency，并记录了输入 SHA-256。
