import { WorkspaceHeader } from "../../components/layout/WorkspaceHeader";

import { TwinWorkspaceSection } from "./TwinWorkspaceSection";

const twinHighlights = [
  {
    label: "场景节点",
    value: "9 个",
    note: "已拆分台基、殿身、屋面和檐柱等核心结构节点"
  },
  {
    label: "风险点位",
    value: "4 处",
    note: "支持点位与构件档案双向切换"
  },
  {
    label: "联动能力",
    value: "已接通",
    note: "构件档案、病害点位和空间坐标保持联动"
  }
];

function TwinWorkspacePage() {
  return (
    <div className="workspace-page">
      <WorkspaceHeader
        currentModuleId="twin"
        description="查看古建筑空间场景、构件档案和病害坐标。"
        eyebrow="数字档案"
        status="已连接"
        title="数字档案"
      />

      <section className="panel workspace-highlight-panel">
        <div className="workspace-highlight-grid">
          {twinHighlights.map((item) => (
            <article className="workspace-highlight-card" key={item.label}>
              <span>{item.label}</span>
              <strong>{item.value}</strong>
              <p>{item.note}</p>
            </article>
          ))}
        </div>
      </section>

      <TwinWorkspaceSection />
    </div>
  );
}

export default TwinWorkspacePage;
