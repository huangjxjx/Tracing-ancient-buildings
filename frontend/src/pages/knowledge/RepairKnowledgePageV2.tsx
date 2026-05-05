import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import {
  getKnowledgePage,
  getKnowledgeRecommendations,
  type KnowledgePagePayload,
  type KnowledgeRecommendation
} from "../../api/knowledge";
import { WorkspaceHeader } from "../../components/layout/WorkspaceHeader";

function RepairKnowledgePageV2() {
  const [data, setData] = useState<KnowledgePagePayload | null>(null);
  const [recommendations, setRecommendations] = useState<KnowledgeRecommendation[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;

    Promise.all([getKnowledgePage(), getKnowledgeRecommendations().catch(() => ({ items: [], total: 0 }))])
      .then(([payload, recommendationPayload]) => {
        if (!cancelled) {
          setData(payload);
          setRecommendations(
            payload.knowledgeRecommendations.length > 0 ? payload.knowledgeRecommendations : recommendationPayload.items
          );
          setError("");
        }
      })
      .catch((requestError: unknown) => {
        if (!cancelled) {
          setError(requestError instanceof Error ? requestError.message : "知识库加载失败");
        }
      });

    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div className="page-stack">
      <WorkspaceHeader
        currentModuleId="knowledge"
        description="按每条病害档案给出处理方法、复核清单、相关规范和文献参考。"
        eyebrow="处理方法"
        status={data ? "已连接后端" : "读取中"}
        title="档案处理知识"
      />

      {error ? <div className="error-state">后端接口暂时不可用：{error}</div> : null}

      <section className="action-panel">
        <div>
          <h2>按档案看处理方法</h2>
          <p>每条推荐都对应一条检测生成的病害档案，包含处理建议、复核清单和参考资料。</p>
        </div>
        <div className="button-row">
          <Link className="btn secondary" to="/damage-workspace">
            上传检测
          </Link>
          <Link className="btn ghost" to="/regional-screen">
            看监管进度
          </Link>
        </div>
      </section>

      <section className="grid grid-4">
        <article className="card compact">
          <h3>推荐</h3>
          <strong className="metric-value">{recommendations.length || "-"}</strong>
          <span className="metric-note">来自病害档案</span>
        </article>
        <article className="card compact">
          <h3>标准</h3>
          <strong className="metric-value">{data?.knowledgeStandards.length ?? "-"}</strong>
          <span className="metric-note">规范和文献</span>
        </article>
        <article className="card compact">
          <h3>案例</h3>
          <strong className="metric-value">{data?.knowledgeCases.length ?? "-"}</strong>
          <span className="metric-note">相似处理经验</span>
        </article>
        <article className="card compact">
          <h3>清单</h3>
          <strong className="metric-value">{data?.knowledgeChecklists.length ?? "-"}</strong>
          <span className="metric-note">现场复核项</span>
        </article>
      </section>

      <section className="main-grid">
        <div className="card">
          <div className="section-head">
            <div>
              <h2>推荐处理</h2>
              <p>优先看这里。每条对应一个病害档案。</p>
            </div>
          </div>
          <div className="list">
            {recommendations.length > 0 ? (
              recommendations.slice(0, 6).map((item, index) => (
                <div className="list-item" key={`${item.resultId}-${index}`}>
                  <span className="step-number">{index + 1}</span>
                  <div>
                    <div className="row-between">
                      <h3>{item.title}</h3>
                      <span className="status-chip">{item.severity || "待定"}</span>
                    </div>
                    <p>{item.recommendedAction}</p>
                    <span className="metric-note">档案编号：{item.resultId}</span>
                    <span className="metric-note">触发原因：{item.triggerReason}</span>
                    <span className="metric-note">建议标准：{item.suggestedStandard}</span>
                    <span className="metric-note">复核清单：{item.checklistTitle}</span>
                  </div>
                </div>
              ))
            ) : (
              <div className="empty-state">暂无推荐。先在“图片检测与档案生成”页面上传图片。</div>
            )}
          </div>
        </div>

      </section>

      <section className="main-grid">
        <div className="card">
          <div className="section-head">
            <div>
              <h2>规范与文献参考</h2>
              <p>处理方法背后的标准、案例和资料来源。</p>
            </div>
          </div>
          <div className="grid grid-2">
            {recommendations.slice(0, 6).map((item, index) => (
              <article className="card compact" key={`${item.resultId}-references-${index}`}>
                <div className="row-between">
                  <h3>{item.title}</h3>
                  <span className="status-chip">参考</span>
                </div>
                <p style={{ marginTop: "0.35rem" }}>{item.references[0]?.excerpt ?? item.recommendedAction}</p>
                <span className="metric-note">建议依据：{item.suggestedStandard}</span>
                {item.references.slice(0, 3).map((reference) => (
                  <a className="metric-note reference-link" href={reference.url} key={reference.title} rel="noreferrer" target="_blank">
                    {reference.title}
                  </a>
                ))}
              </article>
            ))}
            {!recommendations.length
              ? data?.knowledgeStandards.slice(0, 6).map((item, index) => (
                  <article className="card compact" key={`${item.title}-${index}`}>
                    <div className="row-between">
                      <h3>{item.title}</h3>
                      <span className="status-chip">标准</span>
                    </div>
                    <p style={{ marginTop: "0.35rem" }}>{item.applicableTo}</p>
                    <span className="metric-note">检查点：{item.checkpoints.length}</span>
                  </article>
                ))
              : null}
          </div>
        </div>

        <aside className="card">
          <div className="section-head">
            <div>
              <h2>复核清单</h2>
              <p>到现场时按项确认。</p>
            </div>
          </div>
          <div className="list">
            {data?.knowledgeChecklists.slice(0, 4).map((item, index) => (
              <div className="list-item" key={`${item.title}-${index}`}>
                <span className="step-number">{index + 1}</span>
                <div>
                  <h3>{item.title}</h3>
                  <p>{item.items[0] ?? "按清单完成现场复核。"}</p>
                  <span className="metric-note">包含 {item.items.length} 个现场检查项</span>
                </div>
              </div>
            )) ?? <div className="loading-state">正在读取清单...</div>}
          </div>
        </aside>
      </section>
    </div>
  );
}

export default RepairKnowledgePageV2;
