# Heterogeneous-cost replay analysis

Dense/Sparse per-entry cost ratios are synthetic sensitivity conditions, not latency. At each ratio the target cost preserves feasibility of the corresponding equal-depth state.

## nAUC-cert over log charged cost

| Dataset | Dense:Sparse cost | Policy | Mean | Median | P10 |
|---|---:|---|---:|---:|---:|
| msmarco-passage-trec-dl-2019 | 0.0625 | allocation-grid-envelope | 0.3810 | 0.3101 | 0.0989 |
| msmarco-passage-trec-dl-2019 | 0.0625 | blocker-per-cost | 0.3737 | 0.3069 | 0.0988 |
| msmarco-passage-trec-dl-2019 | 0.0625 | candidate-per-cost | 0.3721 | 0.3069 | 0.0987 |
| msmarco-passage-trec-dl-2019 | 0.0625 | cost-balanced | 0.3375 | 0.2926 | 0.0946 |
| msmarco-passage-trec-dl-2019 | 0.0625 | pressure-per-cost | 0.3741 | 0.3069 | 0.0988 |
| msmarco-passage-trec-dl-2019 | 0.0625 | upper-per-cost | 0.3655 | 0.3085 | 0.0981 |
| msmarco-passage-trec-dl-2019 | 0.125 | allocation-grid-envelope | 0.3800 | 0.3101 | 0.0989 |
| msmarco-passage-trec-dl-2019 | 0.125 | blocker-per-cost | 0.3721 | 0.3069 | 0.0988 |
| msmarco-passage-trec-dl-2019 | 0.125 | candidate-per-cost | 0.3705 | 0.3069 | 0.0987 |
| msmarco-passage-trec-dl-2019 | 0.125 | cost-balanced | 0.3344 | 0.2885 | 0.0942 |
| msmarco-passage-trec-dl-2019 | 0.125 | pressure-per-cost | 0.3724 | 0.3069 | 0.0988 |
| msmarco-passage-trec-dl-2019 | 0.125 | upper-per-cost | 0.3611 | 0.3025 | 0.0974 |
| msmarco-passage-trec-dl-2019 | 0.25 | allocation-grid-envelope | 0.3756 | 0.3069 | 0.0989 |
| msmarco-passage-trec-dl-2019 | 0.25 | blocker-per-cost | 0.3694 | 0.3053 | 0.0988 |
| msmarco-passage-trec-dl-2019 | 0.25 | candidate-per-cost | 0.3675 | 0.2986 | 0.0984 |
| msmarco-passage-trec-dl-2019 | 0.25 | cost-balanced | 0.3393 | 0.2890 | 0.0928 |
| msmarco-passage-trec-dl-2019 | 0.25 | pressure-per-cost | 0.3695 | 0.3053 | 0.0984 |
| msmarco-passage-trec-dl-2019 | 0.25 | upper-per-cost | 0.3558 | 0.2882 | 0.0973 |
| msmarco-passage-trec-dl-2019 | 0.5 | allocation-grid-envelope | 0.3713 | 0.3053 | 0.0981 |
| msmarco-passage-trec-dl-2019 | 0.5 | blocker-per-cost | 0.3665 | 0.3022 | 0.0978 |
| msmarco-passage-trec-dl-2019 | 0.5 | candidate-per-cost | 0.3650 | 0.2986 | 0.0972 |
| msmarco-passage-trec-dl-2019 | 0.5 | cost-balanced | 0.3469 | 0.2874 | 0.0974 |
| msmarco-passage-trec-dl-2019 | 0.5 | pressure-per-cost | 0.3667 | 0.3022 | 0.0978 |
| msmarco-passage-trec-dl-2019 | 0.5 | upper-per-cost | 0.3539 | 0.2872 | 0.0975 |
| msmarco-passage-trec-dl-2019 | 1 | allocation-grid-envelope | 0.3680 | 0.3001 | 0.0975 |
| msmarco-passage-trec-dl-2019 | 1 | blocker-per-cost | 0.3629 | 0.2986 | 0.0975 |
| msmarco-passage-trec-dl-2019 | 1 | candidate-per-cost | 0.3613 | 0.2933 | 0.0954 |
| msmarco-passage-trec-dl-2019 | 1 | cost-balanced | 0.3456 | 0.2832 | 0.0972 |
| msmarco-passage-trec-dl-2019 | 1 | pressure-per-cost | 0.3629 | 0.2986 | 0.0975 |
| msmarco-passage-trec-dl-2019 | 1 | upper-per-cost | 0.3456 | 0.2832 | 0.0972 |
| msmarco-passage-trec-dl-2019 | 2 | allocation-grid-envelope | 0.3634 | 0.3006 | 0.0975 |
| msmarco-passage-trec-dl-2019 | 2 | blocker-per-cost | 0.3598 | 0.2990 | 0.0975 |
| msmarco-passage-trec-dl-2019 | 2 | candidate-per-cost | 0.3584 | 0.2985 | 0.0954 |
| msmarco-passage-trec-dl-2019 | 2 | cost-balanced | 0.3361 | 0.2905 | 0.0909 |
| msmarco-passage-trec-dl-2019 | 2 | pressure-per-cost | 0.3594 | 0.2990 | 0.0972 |
| msmarco-passage-trec-dl-2019 | 2 | upper-per-cost | 0.3425 | 0.2872 | 0.0934 |
| msmarco-passage-trec-dl-2019 | 4 | allocation-grid-envelope | 0.3628 | 0.2990 | 0.0972 |
| msmarco-passage-trec-dl-2019 | 4 | blocker-per-cost | 0.3585 | 0.2958 | 0.0972 |
| msmarco-passage-trec-dl-2019 | 4 | candidate-per-cost | 0.3571 | 0.2958 | 0.0947 |
| msmarco-passage-trec-dl-2019 | 4 | cost-balanced | 0.3223 | 0.2863 | 0.0893 |
| msmarco-passage-trec-dl-2019 | 4 | pressure-per-cost | 0.3584 | 0.2958 | 0.0972 |
| msmarco-passage-trec-dl-2019 | 4 | upper-per-cost | 0.3412 | 0.2910 | 0.0920 |
| msmarco-passage-trec-dl-2019 | 8 | allocation-grid-envelope | 0.3627 | 0.3047 | 0.0972 |
| msmarco-passage-trec-dl-2019 | 8 | blocker-per-cost | 0.3583 | 0.2983 | 0.0972 |
| msmarco-passage-trec-dl-2019 | 8 | candidate-per-cost | 0.3568 | 0.2958 | 0.0947 |
| msmarco-passage-trec-dl-2019 | 8 | cost-balanced | 0.3160 | 0.2826 | 0.0864 |
| msmarco-passage-trec-dl-2019 | 8 | pressure-per-cost | 0.3587 | 0.2999 | 0.0972 |
| msmarco-passage-trec-dl-2019 | 8 | upper-per-cost | 0.3412 | 0.2910 | 0.0920 |
| msmarco-passage-trec-dl-2019 | 16 | allocation-grid-envelope | 0.3617 | 0.3047 | 0.0972 |
| msmarco-passage-trec-dl-2019 | 16 | blocker-per-cost | 0.3580 | 0.2999 | 0.0972 |
| msmarco-passage-trec-dl-2019 | 16 | candidate-per-cost | 0.3566 | 0.2958 | 0.0960 |
| msmarco-passage-trec-dl-2019 | 16 | cost-balanced | 0.3171 | 0.2815 | 0.0867 |
| msmarco-passage-trec-dl-2019 | 16 | pressure-per-cost | 0.3583 | 0.2999 | 0.0972 |
| msmarco-passage-trec-dl-2019 | 16 | upper-per-cost | 0.3449 | 0.2969 | 0.0922 |
| msmarco-passage-trec-dl-2020 | 0.0625 | allocation-grid-envelope | 0.3212 | 0.3016 | 0.1171 |
| msmarco-passage-trec-dl-2020 | 0.0625 | blocker-per-cost | 0.3161 | 0.2976 | 0.1164 |
| msmarco-passage-trec-dl-2020 | 0.0625 | candidate-per-cost | 0.3149 | 0.2976 | 0.1119 |
| msmarco-passage-trec-dl-2020 | 0.0625 | cost-balanced | 0.2858 | 0.2562 | 0.1120 |
| msmarco-passage-trec-dl-2020 | 0.0625 | pressure-per-cost | 0.3165 | 0.2976 | 0.1164 |
| msmarco-passage-trec-dl-2020 | 0.0625 | upper-per-cost | 0.3087 | 0.2873 | 0.1161 |
| msmarco-passage-trec-dl-2020 | 0.125 | allocation-grid-envelope | 0.3205 | 0.3032 | 0.1171 |
| msmarco-passage-trec-dl-2020 | 0.125 | blocker-per-cost | 0.3146 | 0.2936 | 0.1164 |
| msmarco-passage-trec-dl-2020 | 0.125 | candidate-per-cost | 0.3132 | 0.2936 | 0.1119 |
| msmarco-passage-trec-dl-2020 | 0.125 | cost-balanced | 0.2850 | 0.2602 | 0.1115 |
| msmarco-passage-trec-dl-2020 | 0.125 | pressure-per-cost | 0.3150 | 0.2936 | 0.1164 |
| msmarco-passage-trec-dl-2020 | 0.125 | upper-per-cost | 0.3020 | 0.2809 | 0.1161 |
| msmarco-passage-trec-dl-2020 | 0.25 | allocation-grid-envelope | 0.3177 | 0.2992 | 0.1178 |
| msmarco-passage-trec-dl-2020 | 0.25 | blocker-per-cost | 0.3137 | 0.2952 | 0.1159 |
| msmarco-passage-trec-dl-2020 | 0.25 | candidate-per-cost | 0.3123 | 0.2952 | 0.1136 |
| msmarco-passage-trec-dl-2020 | 0.25 | cost-balanced | 0.2873 | 0.2496 | 0.1120 |
| msmarco-passage-trec-dl-2020 | 0.25 | pressure-per-cost | 0.3136 | 0.2952 | 0.1164 |
| msmarco-passage-trec-dl-2020 | 0.25 | upper-per-cost | 0.3007 | 0.2817 | 0.1161 |
| msmarco-passage-trec-dl-2020 | 0.5 | allocation-grid-envelope | 0.3162 | 0.2992 | 0.1178 |
| msmarco-passage-trec-dl-2020 | 0.5 | blocker-per-cost | 0.3132 | 0.2960 | 0.1159 |
| msmarco-passage-trec-dl-2020 | 0.5 | candidate-per-cost | 0.3116 | 0.2960 | 0.1143 |
| msmarco-passage-trec-dl-2020 | 0.5 | cost-balanced | 0.2931 | 0.2575 | 0.1139 |
| msmarco-passage-trec-dl-2020 | 0.5 | pressure-per-cost | 0.3132 | 0.2960 | 0.1159 |
| msmarco-passage-trec-dl-2020 | 0.5 | upper-per-cost | 0.2997 | 0.2809 | 0.1161 |
| msmarco-passage-trec-dl-2020 | 1 | allocation-grid-envelope | 0.3137 | 0.3040 | 0.1183 |
| msmarco-passage-trec-dl-2020 | 1 | blocker-per-cost | 0.3112 | 0.3000 | 0.1183 |
| msmarco-passage-trec-dl-2020 | 1 | candidate-per-cost | 0.3098 | 0.3000 | 0.1150 |
| msmarco-passage-trec-dl-2020 | 1 | cost-balanced | 0.2976 | 0.2852 | 0.1146 |
| msmarco-passage-trec-dl-2020 | 1 | pressure-per-cost | 0.3112 | 0.3000 | 0.1183 |
| msmarco-passage-trec-dl-2020 | 1 | upper-per-cost | 0.2976 | 0.2852 | 0.1146 |
| msmarco-passage-trec-dl-2020 | 2 | allocation-grid-envelope | 0.3121 | 0.3056 | 0.1187 |
| msmarco-passage-trec-dl-2020 | 2 | blocker-per-cost | 0.3090 | 0.3024 | 0.1183 |
| msmarco-passage-trec-dl-2020 | 2 | candidate-per-cost | 0.3078 | 0.2976 | 0.1160 |
| msmarco-passage-trec-dl-2020 | 2 | cost-balanced | 0.2923 | 0.2768 | 0.1143 |
| msmarco-passage-trec-dl-2020 | 2 | pressure-per-cost | 0.3091 | 0.3024 | 0.1183 |
| msmarco-passage-trec-dl-2020 | 2 | upper-per-cost | 0.2982 | 0.2923 | 0.1158 |
| msmarco-passage-trec-dl-2020 | 4 | allocation-grid-envelope | 0.3097 | 0.3054 | 0.1176 |
| msmarco-passage-trec-dl-2020 | 4 | blocker-per-cost | 0.3073 | 0.3011 | 0.1173 |
| msmarco-passage-trec-dl-2020 | 4 | candidate-per-cost | 0.3060 | 0.3011 | 0.1154 |
| msmarco-passage-trec-dl-2020 | 4 | cost-balanced | 0.2820 | 0.2688 | 0.1110 |
| msmarco-passage-trec-dl-2020 | 4 | pressure-per-cost | 0.3074 | 0.3011 | 0.1170 |
| msmarco-passage-trec-dl-2020 | 4 | upper-per-cost | 0.2941 | 0.2915 | 0.1148 |
| msmarco-passage-trec-dl-2020 | 8 | allocation-grid-envelope | 0.3093 | 0.3078 | 0.1172 |
| msmarco-passage-trec-dl-2020 | 8 | blocker-per-cost | 0.3073 | 0.3034 | 0.1167 |
| msmarco-passage-trec-dl-2020 | 8 | candidate-per-cost | 0.3062 | 0.3042 | 0.1164 |
| msmarco-passage-trec-dl-2020 | 8 | cost-balanced | 0.2756 | 0.2650 | 0.1096 |
| msmarco-passage-trec-dl-2020 | 8 | pressure-per-cost | 0.3073 | 0.3034 | 0.1167 |
| msmarco-passage-trec-dl-2020 | 8 | upper-per-cost | 0.2936 | 0.2899 | 0.1137 |
| msmarco-passage-trec-dl-2020 | 16 | allocation-grid-envelope | 0.3093 | 0.3099 | 0.1172 |
| msmarco-passage-trec-dl-2020 | 16 | blocker-per-cost | 0.3074 | 0.3053 | 0.1167 |
| msmarco-passage-trec-dl-2020 | 16 | candidate-per-cost | 0.3064 | 0.3061 | 0.1167 |
| msmarco-passage-trec-dl-2020 | 16 | cost-balanced | 0.2770 | 0.2642 | 0.1127 |
| msmarco-passage-trec-dl-2020 | 16 | pressure-per-cost | 0.3075 | 0.3053 | 0.1172 |
| msmarco-passage-trec-dl-2020 | 16 | upper-per-cost | 0.2962 | 0.2956 | 0.1142 |

## Mean certified prefix at base budget 2,048

| Dataset | Dense:Sparse cost | Policy | Mean K |
|---|---:|---|---:|
| msmarco-passage-trec-dl-2019 | 0.0625 | allocation-grid-envelope | 47.721 |
| msmarco-passage-trec-dl-2019 | 0.0625 | blocker-per-cost | 47.721 |
| msmarco-passage-trec-dl-2019 | 0.0625 | candidate-per-cost | 47.558 |
| msmarco-passage-trec-dl-2019 | 0.0625 | cost-balanced | 45.837 |
| msmarco-passage-trec-dl-2019 | 0.0625 | pressure-per-cost | 47.721 |
| msmarco-passage-trec-dl-2019 | 0.0625 | upper-per-cost | 45.419 |
| msmarco-passage-trec-dl-2019 | 0.125 | allocation-grid-envelope | 47.884 |
| msmarco-passage-trec-dl-2019 | 0.125 | blocker-per-cost | 47.442 |
| msmarco-passage-trec-dl-2019 | 0.125 | candidate-per-cost | 47.302 |
| msmarco-passage-trec-dl-2019 | 0.125 | cost-balanced | 42.651 |
| msmarco-passage-trec-dl-2019 | 0.125 | pressure-per-cost | 47.442 |
| msmarco-passage-trec-dl-2019 | 0.125 | upper-per-cost | 45.140 |
| msmarco-passage-trec-dl-2019 | 0.25 | allocation-grid-envelope | 47.163 |
| msmarco-passage-trec-dl-2019 | 0.25 | blocker-per-cost | 46.953 |
| msmarco-passage-trec-dl-2019 | 0.25 | candidate-per-cost | 46.605 |
| msmarco-passage-trec-dl-2019 | 0.25 | cost-balanced | 43.233 |
| msmarco-passage-trec-dl-2019 | 0.25 | pressure-per-cost | 46.860 |
| msmarco-passage-trec-dl-2019 | 0.25 | upper-per-cost | 44.791 |
| msmarco-passage-trec-dl-2019 | 0.5 | allocation-grid-envelope | 46.814 |
| msmarco-passage-trec-dl-2019 | 0.5 | blocker-per-cost | 46.721 |
| msmarco-passage-trec-dl-2019 | 0.5 | candidate-per-cost | 46.465 |
| msmarco-passage-trec-dl-2019 | 0.5 | cost-balanced | 42.512 |
| msmarco-passage-trec-dl-2019 | 0.5 | pressure-per-cost | 46.721 |
| msmarco-passage-trec-dl-2019 | 0.5 | upper-per-cost | 43.605 |
| msmarco-passage-trec-dl-2019 | 1 | allocation-grid-envelope | 46.163 |
| msmarco-passage-trec-dl-2019 | 1 | blocker-per-cost | 45.581 |
| msmarco-passage-trec-dl-2019 | 1 | candidate-per-cost | 45.349 |
| msmarco-passage-trec-dl-2019 | 1 | cost-balanced | 41.860 |
| msmarco-passage-trec-dl-2019 | 1 | pressure-per-cost | 45.558 |
| msmarco-passage-trec-dl-2019 | 1 | upper-per-cost | 41.860 |
| msmarco-passage-trec-dl-2019 | 2 | allocation-grid-envelope | 44.953 |
| msmarco-passage-trec-dl-2019 | 2 | blocker-per-cost | 44.837 |
| msmarco-passage-trec-dl-2019 | 2 | candidate-per-cost | 44.628 |
| msmarco-passage-trec-dl-2019 | 2 | cost-balanced | 40.837 |
| msmarco-passage-trec-dl-2019 | 2 | pressure-per-cost | 44.535 |
| msmarco-passage-trec-dl-2019 | 2 | upper-per-cost | 41.930 |
| msmarco-passage-trec-dl-2019 | 4 | allocation-grid-envelope | 44.535 |
| msmarco-passage-trec-dl-2019 | 4 | blocker-per-cost | 44.488 |
| msmarco-passage-trec-dl-2019 | 4 | candidate-per-cost | 44.302 |
| msmarco-passage-trec-dl-2019 | 4 | cost-balanced | 39.326 |
| msmarco-passage-trec-dl-2019 | 4 | pressure-per-cost | 44.209 |
| msmarco-passage-trec-dl-2019 | 4 | upper-per-cost | 41.907 |
| msmarco-passage-trec-dl-2019 | 8 | allocation-grid-envelope | 45.023 |
| msmarco-passage-trec-dl-2019 | 8 | blocker-per-cost | 44.814 |
| msmarco-passage-trec-dl-2019 | 8 | candidate-per-cost | 44.721 |
| msmarco-passage-trec-dl-2019 | 8 | cost-balanced | 38.488 |
| msmarco-passage-trec-dl-2019 | 8 | pressure-per-cost | 44.814 |
| msmarco-passage-trec-dl-2019 | 8 | upper-per-cost | 42.233 |
| msmarco-passage-trec-dl-2019 | 16 | allocation-grid-envelope | 44.698 |
| msmarco-passage-trec-dl-2019 | 16 | blocker-per-cost | 44.698 |
| msmarco-passage-trec-dl-2019 | 16 | candidate-per-cost | 44.581 |
| msmarco-passage-trec-dl-2019 | 16 | cost-balanced | 41.837 |
| msmarco-passage-trec-dl-2019 | 16 | pressure-per-cost | 44.698 |
| msmarco-passage-trec-dl-2019 | 16 | upper-per-cost | 43.279 |
| msmarco-passage-trec-dl-2020 | 0.0625 | allocation-grid-envelope | 38.074 |
| msmarco-passage-trec-dl-2020 | 0.0625 | blocker-per-cost | 38.037 |
| msmarco-passage-trec-dl-2020 | 0.0625 | candidate-per-cost | 37.870 |
| msmarco-passage-trec-dl-2020 | 0.0625 | cost-balanced | 36.667 |
| msmarco-passage-trec-dl-2020 | 0.0625 | pressure-per-cost | 37.963 |
| msmarco-passage-trec-dl-2020 | 0.0625 | upper-per-cost | 37.148 |
| msmarco-passage-trec-dl-2020 | 0.125 | allocation-grid-envelope | 38.278 |
| msmarco-passage-trec-dl-2020 | 0.125 | blocker-per-cost | 37.667 |
| msmarco-passage-trec-dl-2020 | 0.125 | candidate-per-cost | 37.500 |
| msmarco-passage-trec-dl-2020 | 0.125 | cost-balanced | 35.500 |
| msmarco-passage-trec-dl-2020 | 0.125 | pressure-per-cost | 37.704 |
| msmarco-passage-trec-dl-2020 | 0.125 | upper-per-cost | 36.074 |
| msmarco-passage-trec-dl-2020 | 0.25 | allocation-grid-envelope | 37.907 |
| msmarco-passage-trec-dl-2020 | 0.25 | blocker-per-cost | 37.759 |
| msmarco-passage-trec-dl-2020 | 0.25 | candidate-per-cost | 37.611 |
| msmarco-passage-trec-dl-2020 | 0.25 | cost-balanced | 35.370 |
| msmarco-passage-trec-dl-2020 | 0.25 | pressure-per-cost | 37.722 |
| msmarco-passage-trec-dl-2020 | 0.25 | upper-per-cost | 35.537 |
| msmarco-passage-trec-dl-2020 | 0.5 | allocation-grid-envelope | 38.370 |
| msmarco-passage-trec-dl-2020 | 0.5 | blocker-per-cost | 38.315 |
| msmarco-passage-trec-dl-2020 | 0.5 | candidate-per-cost | 38.185 |
| msmarco-passage-trec-dl-2020 | 0.5 | cost-balanced | 35.204 |
| msmarco-passage-trec-dl-2020 | 0.5 | pressure-per-cost | 38.259 |
| msmarco-passage-trec-dl-2020 | 0.5 | upper-per-cost | 35.389 |
| msmarco-passage-trec-dl-2020 | 1 | allocation-grid-envelope | 38.315 |
| msmarco-passage-trec-dl-2020 | 1 | blocker-per-cost | 38.278 |
| msmarco-passage-trec-dl-2020 | 1 | candidate-per-cost | 38.148 |
| msmarco-passage-trec-dl-2020 | 1 | cost-balanced | 34.907 |
| msmarco-passage-trec-dl-2020 | 1 | pressure-per-cost | 38.278 |
| msmarco-passage-trec-dl-2020 | 1 | upper-per-cost | 34.907 |
| msmarco-passage-trec-dl-2020 | 2 | allocation-grid-envelope | 38.222 |
| msmarco-passage-trec-dl-2020 | 2 | blocker-per-cost | 38.019 |
| msmarco-passage-trec-dl-2020 | 2 | candidate-per-cost | 37.852 |
| msmarco-passage-trec-dl-2020 | 2 | cost-balanced | 36.148 |
| msmarco-passage-trec-dl-2020 | 2 | pressure-per-cost | 38.111 |
| msmarco-passage-trec-dl-2020 | 2 | upper-per-cost | 36.130 |
| msmarco-passage-trec-dl-2020 | 4 | allocation-grid-envelope | 37.759 |
| msmarco-passage-trec-dl-2020 | 4 | blocker-per-cost | 37.759 |
| msmarco-passage-trec-dl-2020 | 4 | candidate-per-cost | 37.537 |
| msmarco-passage-trec-dl-2020 | 4 | cost-balanced | 35.074 |
| msmarco-passage-trec-dl-2020 | 4 | pressure-per-cost | 37.722 |
| msmarco-passage-trec-dl-2020 | 4 | upper-per-cost | 36.611 |
| msmarco-passage-trec-dl-2020 | 8 | allocation-grid-envelope | 37.907 |
| msmarco-passage-trec-dl-2020 | 8 | blocker-per-cost | 37.870 |
| msmarco-passage-trec-dl-2020 | 8 | candidate-per-cost | 37.759 |
| msmarco-passage-trec-dl-2020 | 8 | cost-balanced | 33.907 |
| msmarco-passage-trec-dl-2020 | 8 | pressure-per-cost | 37.852 |
| msmarco-passage-trec-dl-2020 | 8 | upper-per-cost | 36.778 |
| msmarco-passage-trec-dl-2020 | 16 | allocation-grid-envelope | 37.944 |
| msmarco-passage-trec-dl-2020 | 16 | blocker-per-cost | 37.926 |
| msmarco-passage-trec-dl-2020 | 16 | candidate-per-cost | 37.870 |
| msmarco-passage-trec-dl-2020 | 16 | cost-balanced | 36.444 |
| msmarco-passage-trec-dl-2020 | 16 | pressure-per-cost | 37.926 |
| msmarco-passage-trec-dl-2020 | 16 | upper-per-cost | 36.926 |

## Policy wins by query and cost ratio

A win uses query-level nAUC; ties count for every tied policy.

| Dataset | Dense:Sparse cost | Policy | Wins | Queries |
|---|---:|---|---:|---:|
| msmarco-passage-trec-dl-2019 | 0.0625 | allocation-grid-envelope | 43 | 43 |
| msmarco-passage-trec-dl-2019 | 0.0625 | blocker-per-cost | 11 | 43 |
| msmarco-passage-trec-dl-2019 | 0.0625 | candidate-per-cost | 8 | 43 |
| msmarco-passage-trec-dl-2019 | 0.0625 | cost-balanced | 1 | 43 |
| msmarco-passage-trec-dl-2019 | 0.0625 | pressure-per-cost | 12 | 43 |
| msmarco-passage-trec-dl-2019 | 0.0625 | upper-per-cost | 3 | 43 |
| msmarco-passage-trec-dl-2019 | 0.125 | allocation-grid-envelope | 43 | 43 |
| msmarco-passage-trec-dl-2019 | 0.125 | blocker-per-cost | 10 | 43 |
| msmarco-passage-trec-dl-2019 | 0.125 | candidate-per-cost | 8 | 43 |
| msmarco-passage-trec-dl-2019 | 0.125 | cost-balanced | 1 | 43 |
| msmarco-passage-trec-dl-2019 | 0.125 | pressure-per-cost | 11 | 43 |
| msmarco-passage-trec-dl-2019 | 0.125 | upper-per-cost | 2 | 43 |
| msmarco-passage-trec-dl-2019 | 0.25 | allocation-grid-envelope | 43 | 43 |
| msmarco-passage-trec-dl-2019 | 0.25 | blocker-per-cost | 13 | 43 |
| msmarco-passage-trec-dl-2019 | 0.25 | candidate-per-cost | 10 | 43 |
| msmarco-passage-trec-dl-2019 | 0.25 | cost-balanced | 1 | 43 |
| msmarco-passage-trec-dl-2019 | 0.25 | pressure-per-cost | 16 | 43 |
| msmarco-passage-trec-dl-2019 | 0.25 | upper-per-cost | 2 | 43 |
| msmarco-passage-trec-dl-2019 | 0.5 | allocation-grid-envelope | 43 | 43 |
| msmarco-passage-trec-dl-2019 | 0.5 | blocker-per-cost | 11 | 43 |
| msmarco-passage-trec-dl-2019 | 0.5 | candidate-per-cost | 8 | 43 |
| msmarco-passage-trec-dl-2019 | 0.5 | cost-balanced | 3 | 43 |
| msmarco-passage-trec-dl-2019 | 0.5 | pressure-per-cost | 12 | 43 |
| msmarco-passage-trec-dl-2019 | 0.5 | upper-per-cost | 4 | 43 |
| msmarco-passage-trec-dl-2019 | 1 | allocation-grid-envelope | 43 | 43 |
| msmarco-passage-trec-dl-2019 | 1 | blocker-per-cost | 10 | 43 |
| msmarco-passage-trec-dl-2019 | 1 | candidate-per-cost | 6 | 43 |
| msmarco-passage-trec-dl-2019 | 1 | cost-balanced | 5 | 43 |
| msmarco-passage-trec-dl-2019 | 1 | pressure-per-cost | 9 | 43 |
| msmarco-passage-trec-dl-2019 | 1 | upper-per-cost | 5 | 43 |
| msmarco-passage-trec-dl-2019 | 2 | allocation-grid-envelope | 43 | 43 |
| msmarco-passage-trec-dl-2019 | 2 | blocker-per-cost | 12 | 43 |
| msmarco-passage-trec-dl-2019 | 2 | candidate-per-cost | 5 | 43 |
| msmarco-passage-trec-dl-2019 | 2 | cost-balanced | 3 | 43 |
| msmarco-passage-trec-dl-2019 | 2 | pressure-per-cost | 11 | 43 |
| msmarco-passage-trec-dl-2019 | 2 | upper-per-cost | 3 | 43 |
| msmarco-passage-trec-dl-2019 | 4 | allocation-grid-envelope | 43 | 43 |
| msmarco-passage-trec-dl-2019 | 4 | blocker-per-cost | 12 | 43 |
| msmarco-passage-trec-dl-2019 | 4 | candidate-per-cost | 7 | 43 |
| msmarco-passage-trec-dl-2019 | 4 | cost-balanced | 1 | 43 |
| msmarco-passage-trec-dl-2019 | 4 | pressure-per-cost | 13 | 43 |
| msmarco-passage-trec-dl-2019 | 4 | upper-per-cost | 2 | 43 |
| msmarco-passage-trec-dl-2019 | 8 | allocation-grid-envelope | 43 | 43 |
| msmarco-passage-trec-dl-2019 | 8 | blocker-per-cost | 15 | 43 |
| msmarco-passage-trec-dl-2019 | 8 | candidate-per-cost | 12 | 43 |
| msmarco-passage-trec-dl-2019 | 8 | cost-balanced | 1 | 43 |
| msmarco-passage-trec-dl-2019 | 8 | pressure-per-cost | 17 | 43 |
| msmarco-passage-trec-dl-2019 | 8 | upper-per-cost | 2 | 43 |
| msmarco-passage-trec-dl-2019 | 16 | allocation-grid-envelope | 43 | 43 |
| msmarco-passage-trec-dl-2019 | 16 | blocker-per-cost | 21 | 43 |
| msmarco-passage-trec-dl-2019 | 16 | candidate-per-cost | 16 | 43 |
| msmarco-passage-trec-dl-2019 | 16 | cost-balanced | 1 | 43 |
| msmarco-passage-trec-dl-2019 | 16 | pressure-per-cost | 22 | 43 |
| msmarco-passage-trec-dl-2019 | 16 | upper-per-cost | 3 | 43 |
| msmarco-passage-trec-dl-2020 | 0.0625 | allocation-grid-envelope | 54 | 54 |
| msmarco-passage-trec-dl-2020 | 0.0625 | blocker-per-cost | 20 | 54 |
| msmarco-passage-trec-dl-2020 | 0.0625 | candidate-per-cost | 19 | 54 |
| msmarco-passage-trec-dl-2020 | 0.0625 | cost-balanced | 0 | 54 |
| msmarco-passage-trec-dl-2020 | 0.0625 | pressure-per-cost | 19 | 54 |
| msmarco-passage-trec-dl-2020 | 0.0625 | upper-per-cost | 3 | 54 |
| msmarco-passage-trec-dl-2020 | 0.125 | allocation-grid-envelope | 54 | 54 |
| msmarco-passage-trec-dl-2020 | 0.125 | blocker-per-cost | 17 | 54 |
| msmarco-passage-trec-dl-2020 | 0.125 | candidate-per-cost | 13 | 54 |
| msmarco-passage-trec-dl-2020 | 0.125 | cost-balanced | 0 | 54 |
| msmarco-passage-trec-dl-2020 | 0.125 | pressure-per-cost | 16 | 54 |
| msmarco-passage-trec-dl-2020 | 0.125 | upper-per-cost | 2 | 54 |
| msmarco-passage-trec-dl-2020 | 0.25 | allocation-grid-envelope | 54 | 54 |
| msmarco-passage-trec-dl-2020 | 0.25 | blocker-per-cost | 16 | 54 |
| msmarco-passage-trec-dl-2020 | 0.25 | candidate-per-cost | 9 | 54 |
| msmarco-passage-trec-dl-2020 | 0.25 | cost-balanced | 0 | 54 |
| msmarco-passage-trec-dl-2020 | 0.25 | pressure-per-cost | 14 | 54 |
| msmarco-passage-trec-dl-2020 | 0.25 | upper-per-cost | 2 | 54 |
| msmarco-passage-trec-dl-2020 | 0.5 | allocation-grid-envelope | 54 | 54 |
| msmarco-passage-trec-dl-2020 | 0.5 | blocker-per-cost | 17 | 54 |
| msmarco-passage-trec-dl-2020 | 0.5 | candidate-per-cost | 12 | 54 |
| msmarco-passage-trec-dl-2020 | 0.5 | cost-balanced | 0 | 54 |
| msmarco-passage-trec-dl-2020 | 0.5 | pressure-per-cost | 16 | 54 |
| msmarco-passage-trec-dl-2020 | 0.5 | upper-per-cost | 2 | 54 |
| msmarco-passage-trec-dl-2020 | 1 | allocation-grid-envelope | 54 | 54 |
| msmarco-passage-trec-dl-2020 | 1 | blocker-per-cost | 19 | 54 |
| msmarco-passage-trec-dl-2020 | 1 | candidate-per-cost | 13 | 54 |
| msmarco-passage-trec-dl-2020 | 1 | cost-balanced | 7 | 54 |
| msmarco-passage-trec-dl-2020 | 1 | pressure-per-cost | 19 | 54 |
| msmarco-passage-trec-dl-2020 | 1 | upper-per-cost | 7 | 54 |
| msmarco-passage-trec-dl-2020 | 2 | allocation-grid-envelope | 54 | 54 |
| msmarco-passage-trec-dl-2020 | 2 | blocker-per-cost | 16 | 54 |
| msmarco-passage-trec-dl-2020 | 2 | candidate-per-cost | 11 | 54 |
| msmarco-passage-trec-dl-2020 | 2 | cost-balanced | 2 | 54 |
| msmarco-passage-trec-dl-2020 | 2 | pressure-per-cost | 14 | 54 |
| msmarco-passage-trec-dl-2020 | 2 | upper-per-cost | 5 | 54 |
| msmarco-passage-trec-dl-2020 | 4 | allocation-grid-envelope | 54 | 54 |
| msmarco-passage-trec-dl-2020 | 4 | blocker-per-cost | 20 | 54 |
| msmarco-passage-trec-dl-2020 | 4 | candidate-per-cost | 14 | 54 |
| msmarco-passage-trec-dl-2020 | 4 | cost-balanced | 2 | 54 |
| msmarco-passage-trec-dl-2020 | 4 | pressure-per-cost | 19 | 54 |
| msmarco-passage-trec-dl-2020 | 4 | upper-per-cost | 3 | 54 |
| msmarco-passage-trec-dl-2020 | 8 | allocation-grid-envelope | 54 | 54 |
| msmarco-passage-trec-dl-2020 | 8 | blocker-per-cost | 23 | 54 |
| msmarco-passage-trec-dl-2020 | 8 | candidate-per-cost | 17 | 54 |
| msmarco-passage-trec-dl-2020 | 8 | cost-balanced | 1 | 54 |
| msmarco-passage-trec-dl-2020 | 8 | pressure-per-cost | 23 | 54 |
| msmarco-passage-trec-dl-2020 | 8 | upper-per-cost | 3 | 54 |
| msmarco-passage-trec-dl-2020 | 16 | allocation-grid-envelope | 54 | 54 |
| msmarco-passage-trec-dl-2020 | 16 | blocker-per-cost | 29 | 54 |
| msmarco-passage-trec-dl-2020 | 16 | candidate-per-cost | 22 | 54 |
| msmarco-passage-trec-dl-2020 | 16 | cost-balanced | 0 | 54 |
| msmarco-passage-trec-dl-2020 | 16 | pressure-per-cost | 31 | 54 |
| msmarco-passage-trec-dl-2020 | 16 | upper-per-cost | 2 | 54 |

## Headroom to the non-deployable allocation envelope

The strongest single deployable policy is selected by mean query-level nAUC within each condition. Oracle headroom is computed per query before averaging. The best-of-deployable column is an additional non-deployable selector that picks the best policy after seeing each complete query trace.

| Dataset | Cost ratio | Strongest deployable | Mean policy nAUC | Envelope | Gap | Relative gap | Best-of-deployable gap |
|---|---:|---|---:|---:|---:|---:|---:|
| msmarco-passage-trec-dl-2019 | 0.0625 | pressure-per-cost | 0.3741 | 0.3810 | 0.0069 | 1.82% | 0.0065 |
| msmarco-passage-trec-dl-2019 | 0.125 | pressure-per-cost | 0.3724 | 0.3800 | 0.0076 | 2.00% | 0.0075 |
| msmarco-passage-trec-dl-2019 | 0.25 | pressure-per-cost | 0.3695 | 0.3756 | 0.0061 | 1.61% | 0.0058 |
| msmarco-passage-trec-dl-2019 | 0.5 | pressure-per-cost | 0.3667 | 0.3713 | 0.0047 | 1.26% | 0.0038 |
| msmarco-passage-trec-dl-2019 | 1 | blocker-per-cost | 0.3629 | 0.3680 | 0.0051 | 1.39% | 0.0051 |
| msmarco-passage-trec-dl-2019 | 2 | blocker-per-cost | 0.3598 | 0.3634 | 0.0036 | 0.99% | 0.0035 |
| msmarco-passage-trec-dl-2019 | 4 | blocker-per-cost | 0.3585 | 0.3628 | 0.0043 | 1.18% | 0.0036 |
| msmarco-passage-trec-dl-2019 | 8 | pressure-per-cost | 0.3587 | 0.3627 | 0.0040 | 1.12% | 0.0036 |
| msmarco-passage-trec-dl-2019 | 16 | pressure-per-cost | 0.3583 | 0.3617 | 0.0034 | 0.93% | 0.0028 |
| msmarco-passage-trec-dl-2020 | 0.0625 | pressure-per-cost | 0.3165 | 0.3212 | 0.0047 | 1.47% | 0.0042 |
| msmarco-passage-trec-dl-2020 | 0.125 | pressure-per-cost | 0.3150 | 0.3205 | 0.0055 | 1.71% | 0.0053 |
| msmarco-passage-trec-dl-2020 | 0.25 | blocker-per-cost | 0.3137 | 0.3177 | 0.0040 | 1.27% | 0.0037 |
| msmarco-passage-trec-dl-2020 | 0.5 | pressure-per-cost | 0.3132 | 0.3162 | 0.0030 | 0.96% | 0.0027 |
| msmarco-passage-trec-dl-2020 | 1 | blocker-per-cost | 0.3112 | 0.3137 | 0.0025 | 0.79% | 0.0025 |
| msmarco-passage-trec-dl-2020 | 2 | pressure-per-cost | 0.3091 | 0.3121 | 0.0029 | 0.94% | 0.0027 |
| msmarco-passage-trec-dl-2020 | 4 | pressure-per-cost | 0.3074 | 0.3097 | 0.0024 | 0.76% | 0.0022 |
| msmarco-passage-trec-dl-2020 | 8 | pressure-per-cost | 0.3073 | 0.3093 | 0.0020 | 0.65% | 0.0018 |
| msmarco-passage-trec-dl-2020 | 16 | pressure-per-cost | 0.3075 | 0.3093 | 0.0018 | 0.58% | 0.0016 |
