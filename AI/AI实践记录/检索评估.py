"""读取 JSONL 检索结果，计算排序指标并与固定基线比较。"""

import argparse
import hashlib
import json
import math
from pathlib import Path

METRICS = ("precision", "recall", "mrr", "ndcg")
# 报告记录评分规则，和基线比较前先确认规则一致。
PROTOCOL = "retrieval-v1;gain=2^grade-1;precision-denominator=k;unanswerable=excluded"


# relevant 保存相关片段及其等级，ranked_ids 保存检索器返回的顺序。
def score_query(relevant, ranked_ids, k):
    if type(k) is not int or k < 1:
        raise ValueError("k 必须是正整数")
    if not isinstance(relevant, dict) or any(
        not isinstance(key, str) or not key or type(grade) is not int or not 1 <= grade <= 3
        for key, grade in relevant.items()
    ):
        raise ValueError("relevant 必须是非空 ID 到 1～3 等级的映射，或空对象")
    if not isinstance(ranked_ids, list) or any(
        not isinstance(key, str) or not key for key in ranked_ids
    ) or len(set(ranked_ids)) != len(ranked_ids):
        raise ValueError("ranked_ids 必须是无重复的非空字符串数组")
    top = ranked_ids[:k]
    if not relevant:
        # 语料没有答案不等于检索器满分；单独统计拒答/错误回答。
        return {name: None for name in METRICS}
    # Precision 的分母固定为 k，即使返回不足 k 条。Recall 的分母是标注中的相关片段数。
    hits = sum(key in relevant for key in top)
    # rank 从 1 开始；只取首个相关结果的倒数，未命中则为 0。
    rr = next((1 / rank for rank, key in enumerate(top, 1) if key in relevant), 0.0)
    dcg = sum((2 ** relevant.get(key, 0) - 1) / math.log2(rank + 1)
              for rank, key in enumerate(top, 1))
    # 理想排序把高相关等级排前，用于把实际 DCG 归一化。
    ideal = sorted(relevant.values(), reverse=True)[:k]
    idcg = sum((2 ** grade - 1) / math.log2(rank + 1)
               for rank, grade in enumerate(ideal, 1))
    return {"precision": hits / k, "recall": hits / len(relevant),
            "mrr": rr, "ndcg": dcg / idcg}


def evaluate(cases, k):
    if not cases:
        raise ValueError("评价集为空")
    seen, ground_truth, details = set(), [], []
    for case in cases:
        case_id = case["id"]
        if not isinstance(case_id, str) or not case_id or case_id in seen:
            raise ValueError("查询 id 必须是唯一的非空字符串")
        seen.add(case_id)
        for field in ("question", "corpus_version"):
            if not isinstance(case.get(field), str) or not case[field].strip():
                raise ValueError(f"缺少有效 {field}")
        scores = score_query(case["relevant"], case["ranked_ids"], k)
        ground_truth.append({key: case[key] for key in
                             ("id", "question", "corpus_version", "relevant")})
        details.append({"id": case_id, "scores": scores,
                        "ranked_ids": case["ranked_ids"][:k]})
    # 指纹只包含固定问题、标注和语料版本，让不同检索排序仍能公平比较。
    canonical = json.dumps(sorted(ground_truth, key=lambda x: x["id"]),
                           ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    means = {}
    for name in METRICS:
        # 无答案问题用 None 单独标记，汇总时同时保留有效查询数量。
        valid = [row["scores"][name] for row in details if row["scores"][name] is not None]
        means[name] = sum(valid) / len(valid) if valid else None
    return {"protocol": PROTOCOL, "k": k,
            "dataset_sha256": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
            "total_queries": len(cases),
            "answerable_queries": sum(bool(case["relevant"]) for case in cases),
            "means": means, "details": details}


# 先检查数据集和指标口径，再返回发生下降的指标及差值。
def regressions(baseline, current):
    for key in ("protocol", "k", "dataset_sha256"):
        if baseline[key] != current[key]:
            raise ValueError(f"两份报告的 {key} 不一致，不能直接比较")
    drops = {}
    for name in METRICS:
        old, new = baseline["means"][name], current["means"][name]
        if (old is None) != (new is None):
            raise ValueError("有效评价样本不一致")
        if old is not None and new < old - 1e-12:
            drops[name] = {"before": old, "after": new, "delta": new - old}
    return drops


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("cases")
    parser.add_argument("report")
    parser.add_argument("--k", type=int, default=3)
    parser.add_argument("--baseline")
    args = parser.parse_args()
    cases = [json.loads(line) for line in Path(args.cases).read_text(encoding="utf-8").splitlines()
             if line.strip()]
    report = evaluate(cases, args.k)
    drops = {}
    if args.baseline:
        baseline = json.loads(Path(args.baseline).read_text(encoding="utf-8"))
        drops = regressions(baseline, report)
        report["regressions"] = drops
    # 即使指标回退，也先写出报告，方便追查受影响的查询。
    Path(args.report).write_text(json.dumps(report, ensure_ascii=False, indent=2,
                                           allow_nan=False), encoding="utf-8")
    print(json.dumps(report["means"], ensure_ascii=False))
    if drops:
        raise SystemExit("评价回退：检查报告与具体问题，再决定是否接受变更")


if __name__ == "__main__":
    main()
