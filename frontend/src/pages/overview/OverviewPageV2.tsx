import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { getOverviewPage, type OverviewPagePayload } from "../../api/overview";
import { overviewWorkbenchCards } from "../../data/workbenchRegistryData";

function OverviewPageV2() {
  const [data, setData] = useState<OverviewPagePayload | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;

    getOverviewPage()
      .then((payload) => {
        if (!cancelled) {
          setData(payload);
          setError("");
        }
      })
      .catch((requestError: unknown) => {
        if (!cancelled) {
          setError(requestError instanceof Error ? requestError.message : "总览数据加载失败");
        }
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const metrics = [
    { label: "档案节点", value: data ? String(data.archiveNodes.length) : "-", note: "应县木塔构件和病害档案" },
    { label: "监管分区", value: data ? String(data.regionalHealth.length) : "-", note: "佛宫寺片区范围" },
    { label: "风险类型", value: data ? String(data.issueRanking.length) : "-", note: "按数量排序" },
    { label: "处置阶段", value: data ? String(data.workOrders.length) : "-", note: "整体处理进度" }
  ];

  return (
    <div className="page-stack">
      <section className="action-panel">
        <div>
          <h2>应县木塔整体情况</h2>
          <p>汇总建筑档案、病害类型、佛宫寺片区状态和处置进度；具体处理方法在知识页面查看。</p>
        </div>
        <div className="button-row">
          <Link className="btn primary" to="/damage-workspace">
            上传图片检测
          </Link>
          <Link className="btn secondary" to="/regional-screen">
            查看佛宫寺片区
          </Link>
        </div>
      </section>

      {error ? <div className="error-state">后端接口暂时不可用：{error}</div> : null}

      <section className="grid grid-4">
        {metrics.map((item) => (
          <article className="card compact" key={item.label}>
            <h3>{item.label}</h3>
            <strong className="metric-value">{item.value}</strong>
            <span className="metric-note">{item.note}</span>
          </article>
        ))}
      </section>

      <section className="grid grid-4">
        {overviewWorkbenchCards.map((item) => (
          <article className="card" key={item.id}>
            <div className="row-between">
              <span className="eyebrow">{item.stage}</span>
              <span className="status-chip ok">可用</span>
            </div>
            <h3 style={{ marginTop: "0.7rem" }}>{item.title}</h3>
            <p style={{ marginTop: "0.35rem" }}>{item.description}</p>
            <Link className="btn ghost" style={{ marginTop: "0.85rem" }} to={item.path}>
              进入
            </Link>
          </article>
        ))}
      </section>

      <section className="main-grid">
        <div className="card">
          <div className="section-head">
            <div>
              <h2>待关注风险</h2>
              <p>按应县木塔当前病害档案和监管关注度排序。</p>
            </div>
          </div>
          <div className="list">
            {data?.issueRanking.slice(0, 5).map((item, index) => (
              <div className="list-item" key={`${item.name}-${index}`}>
                <span className="step-number">{index + 1}</span>
                <div>
                  <div className="row-between">
                    <h3>{item.name}</h3>
                    <strong>{item.value}</strong>
                  </div>
                  <p>来自应县木塔病害档案和片区监管数据。</p>
                  <div className="progress-track" style={{ marginTop: "0.45rem" }}>
                    <div className="progress-fill" style={{ width: `${Math.min(item.value, 100)}%` }} />
                  </div>
                </div>
              </div>
            )) ?? <div className="loading-state">正在读取风险排行...</div>}
          </div>
        </div>
      </section>
    </div>
  );
}

export default OverviewPageV2;
