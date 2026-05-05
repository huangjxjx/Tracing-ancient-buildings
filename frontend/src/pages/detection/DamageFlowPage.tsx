import DamageFlowWorkbench from "../../features/detection/DamageFlowWorkbench";

function DamageFlowPage() {
  return (
    <div className="app-shell">
      <div className="ambient ambient-left" />
      <div className="ambient ambient-right" />

      <main className="damage-flow-page">
        <header className="damage-flow-topbar">
          <div className="damage-flow-branding">
            <p className="eyebrow">Digital Heritage Protection Platform</p>
            <h1>巡迹古建 · 病害检测工作台</h1>
            <p>面向病害上传、识别结果浏览与详情复核的前端主流程页面。</p>
          </div>

          <div className="damage-flow-meta">
            <article className="meta-card">
              <span>当前模块</span>
              <strong>病害识别流程</strong>
              <p>图像上传、结果复核与联动建议的统一入口。</p>
            </article>
            <article className="meta-card">
              <span>状态覆盖</span>
              <strong>3 种</strong>
              <p>上传前 / 识别中 / 识别完成</p>
            </article>
          </div>
        </header>

        <DamageFlowWorkbench />
      </main>
    </div>
  );
}

export default DamageFlowPage;
