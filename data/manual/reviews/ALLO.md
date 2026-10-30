# ALLO（Allogene Therapeutics）复核草稿报告

## 选定组合

- 资产：cema-cel（cemacabtagene ansegedleucel，曾用名 ALLO-501A），同种异体抗 CD19 CAR-T。
- 适应症：一线治疗后 MRD 阳性的大 B 细胞淋巴瘤（LBCL）巩固治疗。pack 匹配 `CEMACABTAGENE ANSEGEDLEUCEL` / `Large B-cell Lymphoma`。
- 阶段：关键性 2 期 ALPHA3。10-Q 原文："In June 2024, we initiated a pivotal Phase 2 clinical trial (ALPHA3)"。
- 买方：Merck & Co.，偏好第 1 位（肿瘤/血液肿瘤，理想阶段「Phase 2b-注册期」）。交易形式：收购。
- 分数：buyer_fit 2（中，只到标签匹配），stage_match 4，clinical 2。预览构建推导出 catalyst 3（高 / 估算）、dealability 3（partial 封顶），总分 67.5。

### 为什么选 Merck #1

- Merck 画像写明「血液肿瘤资产」与「新标准治疗」。ALPHA3 的对照组是观察，该场景没有获批疗法。
- Allogene 10-K 竞争段落只把 Merck 列为双特异 T 细胞衔接器开发方，没有列出 Merck 的 CD19 CAR-T。
- 没有读 Merck 自身管线。因此记为「未核查组合冲突」。
- buyer_fit 只给 2。画像中「血液肿瘤」是治疗领域标签，「新标准治疗」是结果要求，都不是 §3.1 要求的具体适应症、机制或给药方式。Merck 的技术偏好不含细胞治疗，也够不上 3 分。
- 备选：J&J #1 的技术偏好行写了 CAR-T 与「更低细胞治疗制造负担」，可能支持 3 分；但它的治疗领域行针对 BCMA，CD19 不对应。复核人可权衡。

### 排除的买方

- **BMS #3**：画像（CAR-T/细胞疗法，降低制造复杂度）文字最贴合。但 10-K 原文："In February 2021, BMS obtained FDA approval for its anti-CD19 autologous T cell therapy, Breyanzi® for the treatment of adults with 3rd-line LBCL"。这是同机制、同适应症，所以排除。
- **ALLO-329**（SLE，1 期）：阶段早。10-K 把 BMS、Novartis 列为自身免疫细胞治疗竞争方。没有选它作主推荐。

## 权益状态：partial

最新 10-Q（SEC-0001628280-26-056213）原文：

> "expanded our territory under the Original Servier Agreement to include the European Union and the United Kingdom, and provided for an option to further expand our territory to include China and Japan"
> "waived certain of our rights to elect to convert certain of our license rights to a worldwide license"

Q2 新闻稿（MAN-ALLO-2）原文："Servier has granted Allogene exclusive rights to cema-cel in the U.S., all EU Member States and the United Kingdom."

- Allogene 持有：美国、欧盟、英国。
- 其他地区：文件只写 Allogene 的许可区域。其余地区（包括中国和日本，Allogene 只有扩展选择权）按许可方推断仍在 Servier（推断）。
- 这不是「已授权出去」，而是引进的范围本来就不是全球。按 brief 的定义，最接近 partial。
- 上游：权利经 Servier 转授，来源是 Cellectis。2025-12 的仲裁"affirmed continued licensing rights relating to cema-cel"。
- 风险：2026-04 LTC（Thermo Fisher 子公司）声称终止与 Cellectis 的 TALEN 许可。10-Q 原文："could also affect the Company’s rights with respect to CD19 Products"。
- 对许可方的义务：
  - Servier 美国提成 "low tens to the mid teen percentages"，美国以外 10%。
  - 首个适应症还剩 €60.0M 里程碑。后续适应症与销售另有里程碑。
  - Pfizer 资产转让协议下另有里程碑与提成。
- 没有找到控制权变更需许可方同意的条款。
- 债务：10-Q 没有票据或贷款。pack 中 total_debt 为空是正确的。CIRM 资助只在公司自己选择时才转为贷款。
- 现金跑道：10-Q 原文 "fund operations into the first quarter of 2029"。Q2 新闻稿原文 "currently projects its cash runway into 2029"。

## 下一事件

- ALPHA3 中期 EFS 分析，2027 年中。主要 EFS 分析在 2028 年中，两者都在 24 个月窗口内。
- 已标为 high / estimated。"mid-2027" 不是明确的季度或半年，按 brief 规则记为估算。复核人如认可为明确披露，catalyst 从 3 升到 4。

## 待核实

1. Merck 是否已有 CD19 CAR-T 或同场景（一线 MRD 阳性 LBCL）资产：未核查（只读了 Allogene 10-K 竞争段）。
2. buyer_fit：现按标签匹配给 2。改选 J&J #1 是否更好，需复核人判断。
3. "mid-2027" 现记为 estimated，是否改为 disclosed 由复核人决定。
4. LTC 与 Cellectis 的仲裁结果，以及它对 cema-cel 权利的影响。公司说 "is evaluating the potential impact"。
5. Pfizer 协议下的具体里程碑与提成金额：10-Q 只说见 10-K Note 6，没有在本次读取。
6. 收购方能否取得 Servier 持有的地区（美国、欧盟、英国以外）：文件没有说明。
7. 中期分析的完整数据没有同行评审发表，只有 8-K 披露。

## Pack 的问题

- cema-cel 与 ALLO-501A 是同一个资产，pack 把它们列成两个 program。
  - 10-Q 原文："cema-cel (formerly known as ALLO-501A)"。
- ALLO-501A 的「Relapsed/Refractory Large B Cell Lymphoma」phase2 行，来源是 NCT05714345。这是 ALLO-647 清淋试验，已经终止。
- ALLO-647 是清淋抗体，不是独立资产。10-Q 原文："none of our trials open to enrollment or pipeline programs include ALLO-647"。
- ALLO-501 的 Servier 许可已终止（2025-12 仲裁）。
- 自动组合的事件（CT.gov 2027-12 估算）其实对应入组完成，不是数据读出。公司披露的读出是 2027 年中（中期）和 2028 年中（主要）。

## 用时

约 30 分钟。
