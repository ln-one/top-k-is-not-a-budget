# Citation verification — 2026-09-10

The manuscript cites 13 distinct sources. All 13 have verified identity metadata and a defined role below. No DESA citation was added. EAHR is identified as an arXiv preprint. Citation verification does not establish the novelty of the paper.

Academic-search MCP tools were not available in this session. Primary publisher pages, Crossref's public API, arXiv, author-hosted papers, and official documentation were used instead. Raw Crossref responses are retained in `reference-metadata.json`.

| Key | Status | Verified source | Role |
|---|---|---|---|
| elastic | Verified | https://www.elastic.co/docs/reference/elasticsearch/rest-apis/reciprocal-rank-fusion | `rank_window_size`, independent channel retrieval, and truncated fusion; supports the concrete practice described in Introduction. |
| rrf | Verified | https://doi.org/10.1145/1571941.1572114 (Crossref) | RRF title, three authors, SIGIR 2009, pp. 758–759; rank-fusion definition. |
| nra | Verified | https://doi.org/10.1016/S0022-0000(03)00026-6 (Crossref) | Bounds under sorted access; Fagin, Lotem, Naor, JCSS 66(4), 614–656, 2003. Ordered prefix delivery is described separately in this manuscript. |
| eahr | Verified | https://arxiv.org/abs/2608.07152 | Chunran Zhang, 2026; exact resumable hybrid fusion, fixed-window transfer issue, and difficult requests. The user's own approved Chinese text is the manuscript basis. |
| snra | Verified | https://link.springer.com/chapter/10.1007/978-3-642-00672-2_4 | Five authors and pp. 15–26, APWeb/WAIM 2009; selective access to missing fields of the best competitor. Crossref returned HTTP 429, resolved using publisher metadata and original proceedings. |
| lara | Verified | https://doi.org/10.1109/ICDE.2006.54 and https://i.cs.hku.hk/~dcheung/publication/icde2006.pdf | Four authors, ICDE 2006, article/page 72. Section 5.2 supplies online and incremental output (LARA-IN). Original PDF is 12 pages; the proceedings citation is p. 72, not a fabricated 12-page range. |
| dl19 | Verified | https://arxiv.org/abs/2003.07820 | Five authors, overview of TREC 2019, arXiv publication year 2020. |
| dl20 | Verified | https://arxiv.org/abs/2102.07662 | Four authors, overview of TREC 2020, arXiv publication year 2021. |
| nfcorpus | Verified | https://doi.org/10.1007/978-3-319-30671-1_58 (Crossref) | Boteva et al., ECIR 2016, pp. 716–722. The manuscript's 323-query selection is established by local records. |
| scifact | Verified | https://doi.org/10.18653/v1/2020.emnlp-main.609 (Crossref) | Seven authors, EMNLP 2020, pp. 7534–7550. The 300-query retrieval split is the local frozen benchmark. |
| covid | Verified | https://doi.org/10.1016/j.jbi.2021.103865 (Crossref) | Nine authors, JBI 121, article 103865, 2021. The five-round study's 30 shared queries come from local experiment records. |
| bge | Verified | https://huggingface.co/BAAI/bge-small-en-v1.5 | BAAI's exact model card; cited directly instead of assuming another BGE paper names this model version. |
| bm25 | Verified; metadata conflict resolved | https://www.nowpublishers.com/article/DownloadEBook/INR-019 | Publisher's original front matter confirms vol. 3, no. 4, pp. 333–389 (2009), Robertson and Zaragoza. Crossref returned an inconsistent page field (1–174); the paper uses original publisher pagination. |

No numerical DiBud results are taken from external papers. They come from the frozen repository CSVs; `result-audit.json` records the regenerated table values and prose values. The existing Chinese text is not rewritten by the bibliography workflow.

## Addition — 2026-09-11

Added `azure`: Microsoft, *Hybrid Search Scoring (RRF)—Azure AI Search*, official documentation, accessed September 11, 2026. https://learn.microsoft.com/en-us/azure/search/hybrid-search-ranking . Supports parallel text/vector retrieval, finite per-channel result lists, and RRF merging as an independent implementation alongside Elastic. This is an engineering source, not an additional research paper or a claim of universal adoption. The bibliography now contains 14 cited sources.
