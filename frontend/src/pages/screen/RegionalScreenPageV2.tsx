import { useEffect, useMemo, useState } from "react";

import { getScreenPage, type ScreenPagePayload } from "../../api/screen";
import { WorkspaceHeader } from "../../components/layout/WorkspaceHeader";
import type { ScreenAlertSeverity, ScreenCoverageStatus } from "../../types/screen";

function coverageLabel(status: ScreenCoverageStatus) {
  if (status === "critical") {
    return "重点处置";
  }
  if (status === "watch") {
    return "持续关注";
  }
  return "状态稳定";
}

function coverageClass(status: ScreenCoverageStatus) {
  if (status === "critical") {
    return "high";
  }
  if (status === "watch") {
    return "watch";
  }
  return "stable";
}

function alertLabel(severity: ScreenAlertSeverity) {
  if (severity === "high") {
    return "高";
  }
  if (severity === "medium") {
    return "中";
  }
  return "低";
}

function RegionalScreenPageV2() {
  const [data, setData] = useState<ScreenPagePayload | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;

    getScreenPage()
      .then((payload) => {
        if (!cancelled) {
          setData(payload);
          setError("");
        }
      })
      .catch((requestError: unknown) => {
        if (!cancelled) {
          setError(requestError instanceof Error ? requestError.message : "区域监管数据加载失败");
        }
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const highAlertCount = useMemo(
    () => data?.screenAlerts.filter((item) => item.severity === "high").length ?? 0,
    [data]
  );
  const criticalRegionCount = useMemo(
    () => data?.screenCoverageRegions.filter((item) => item.status === "critical").length ?? 0,
    [data]
  );
  const averageProgress = useMemo(() => {
    if (!data?.screenDispatches.length) {
      return 0;
    }
    return Math.round(data.screenDispatches.reduce((sum, item) => sum + item.progress, 0) / data.screenDispatches.length);
  }, [data]);

  return (
    <div className="page-stack">
      <WorkspaceHeader
        currentModuleId="screen"
        description="监管范围聚焦山西省朔州市应县佛宫寺片区，跟踪应县木塔病害告警、现场派工和闭环进度。"
        eyebrow="监管"
        status={data ? "数据已同步" : "读取中"}
        title="佛宫寺片区监管"
      />

      {error ? <div className="error-state">后端接口暂时不可用：{error}</div> : null}

      <section className="grid grid-4">
        <article className="card compact">
          <h3>监管分区</h3>
          <strong className="metric-value">{data?.screenCoverageRegions.length ?? "-"}</strong>
          <span className="metric-note">佛宫寺片区</span>
        </article>
        <article className="card compact">
          <h3>重点分区</h3>
          <strong className="metric-value">{criticalRegionCount}</strong>
          <span className="metric-note">优先派工</span>
        </article>
        <article className="card compact">
          <h3>高风险告警</h3>
          <strong className="metric-value">{highAlertCount}</strong>
          <span className="metric-note">待复核事项</span>
        </article>
        <article className="card compact">
          <h3>平均进度</h3>
          <strong className="metric-value">{averageProgress}%</strong>
          <span className="metric-note">现场任务</span>
        </article>
      </section>

      <section className="main-grid">
        <div className="card">
          <div className="section-head">
            <div>
              <h2>片区风险</h2>
              <p>按应县木塔本体和周边管理范围划分。</p>
            </div>
          </div>
          <div className="grid grid-2">
            {data?.screenCoverageRegions.map((item) => (
              <article className="card compact" key={item.region}>
                <div className="row-between">
                  <h3>{item.region}</h3>
                  <span className={`status-chip ${coverageClass(item.status)}`}>{coverageLabel(item.status)}</span>
                </div>
                <strong className="metric-value">{item.healthIndex}</strong>
                <span className="metric-note">健康指数 / 100</span>
                <span className="metric-note">高风险点：{item.highRiskCount} 处</span>
                <div className="progress-track" style={{ marginTop: "0.55rem" }}>
                  <div className="progress-fill" style={{ width: `${item.workOrderProgress}%` }} />
                </div>
                <span className="metric-note">处置进度 {item.workOrderProgress}%</span>
              </article>
            )) ?? <div className="loading-state">正在读取片区风险...</div>}
          </div>
        </div>

        <aside className="card">
          <div className="section-head">
            <div>
              <h2>告警列表</h2>
              <p>高风险事项排在前面。</p>
            </div>
          </div>
          <div className="list">
            {data?.screenAlerts.slice(0, 6).map((item, index) => (
              <div className="list-item" key={`${item.title}-${index}`}>
                <span className="step-number">{index + 1}</span>
                <div>
                  <div className="row-between">
                    <h3>{item.title}</h3>
                    <span className={`status-chip ${item.severity}`}>{alertLabel(item.severity)}</span>
                  </div>
                  <p>{item.detail}</p>
                  <span className="metric-note">所属分区：{item.region}</span>
                </div>
              </div>
            )) ?? <div className="loading-state">正在读取告警...</div>}
          </div>
        </aside>
      </section>

      <section className="main-grid">
        <div className="card">
          <div className="section-head">
            <div>
              <h2>现场派工</h2>
              <p>查看各队伍当前任务和推进比例。</p>
            </div>
          </div>
          <div className="list">
            {data?.screenDispatches.map((item, index) => (
              <div className="list-item" key={`${item.team}-${item.region}`}>
                <span className="step-number">{index + 1}</span>
                <div>
                  <div className="row-between">
                    <h3>{item.team}</h3>
                    <strong>{item.progress}%</strong>
                  </div>
                  <p>{item.mission}</p>
                  <span className="metric-note">{item.region}</span>
                  <div className="progress-track" style={{ marginTop: "0.45rem" }}>
                    <div className="progress-fill" style={{ width: `${item.progress}%` }} />
                  </div>
                </div>
              </div>
            )) ?? <div className="loading-state">正在读取派工...</div>}
          </div>
        </div>

        <aside className="card">
          <div className="section-head">
            <div>
              <h2>主要问题</h2>
              <p>按风险评分排序。</p>
            </div>
          </div>
          <div className="list">
            {data?.screenIssuesTop5.map((item, index) => (
              <div className="list-item" key={`${item.label}-${index}`}>
                <span className="step-number">{index + 1}</span>
                <div>
                  <div className="row-between">
                    <h3>{item.label}</h3>
                    <strong>{item.value}</strong>
                  </div>
                  <span className="metric-note">{item.count}</span>
                  <div className="progress-track" style={{ marginTop: "0.45rem" }}>
                    <div className="progress-fill" style={{ width: `${Math.min(item.value, 100)}%` }} />
                  </div>
                </div>
              </div>
            )) ?? <div className="loading-state">正在读取问题排行...</div>}
          </div>
        </aside>
      </section>

      <section className="main-grid">
        <div className="card">
          <div className="section-head">
            <div>
              <h2>分区处置要点</h2>
              <p>给现场队伍和管理人员看的当前行动。</p>
            </div>
          </div>
          <div className="list">
            {data?.screenRegionDetails.map((item) => (
              <div className="list-item" key={item.region}>
                <span className="step-number">区</span>
                <div>
                  <div className="row-between">
                    <h3>{item.region}</h3>
                    <span className="status-chip">{item.responseMode}</span>
                  </div>
                  <p>{item.nextAction}</p>
                  <span className="metric-note">{item.commanderWindow}</span>
                  <span className="metric-note">关注：{item.focus}</span>
                </div>
              </div>
            )) ?? <div className="loading-state">正在读取分区处置要点...</div>}
          </div>
        </div>

        <aside className="card">
          <div className="section-head">
            <div>
              <h2>联动记录</h2>
              <p>展示检测、档案、知识和监管之间的同步。</p>
            </div>
          </div>
          <div className="list">
            {data?.screenEvents.map((item) => (
              <div className="list-item" key={`${item.time}-${item.title}`}>
                <span className="step-number">{item.time}</span>
                <div>
                  <div className="row-between">
                    <h3>{item.title}</h3>
                    <span className="status-chip">{item.type}</span>
                  </div>
                  <p>{item.detail}</p>
                </div>
              </div>
            )) ?? <div className="loading-state">正在读取联动记录...</div>}
          </div>
        </aside>
      </section>
    </div>
  );
}

export default RegionalScreenPageV2;
