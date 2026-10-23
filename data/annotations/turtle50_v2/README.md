# 当前发布题库与 partial score

本目录随代码发布，clone/pull 后无需下载原 XLSX 或单独解压数据包。

- `private.json`：TS001–TS050，50 道英文题的汤面、汤底、161 个评分点、权重、满分／半分／零分条件、完整叙事要求和评分说明。可直接传给 `--dataset`。
- `review.md`：逐题人工阅读版，与 JSON 内容一致。
- `../../host_packs/`：`configs/host_bindings.json` 绑定的全部专属 host 示例和事实；当前 15 题有专属包，其余使用本题参考答案和完成条件，均可运行。

`private` 表示这些内容只给 host／grader、不给 player，不表示它们不在 Git 中。实验框架隔离 player 输入；请不要手工把汤底或评分清单放进 player prompt。

原始 49 题 XLSX 保持未改写，其文件名与 SHA-256 记录在 JSON 的 source 字段；TS040 为先前补入的题目。最终评分由三个独立 AI 提案和主 agent 裁定而来，含 annotation_provenance，属于待人工确认的标注，不是人工金标准。评分权重是研究选择，不声称唯一最优。修改评分后需新建实验批次，勿混算不同版本。

所有题可运行不代表每题 host 均有充足人工问答、或已验证高准确率。运行方式与全部参数见 [同事指南](../../../docs/coworker_quickstart.md)。模型账号／API key 仍由运行者自己配置；不在仓库内。
