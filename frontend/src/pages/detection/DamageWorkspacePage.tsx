import { WorkspaceHeader } from "../../components/layout/WorkspaceHeader";
import DamageFlowWorkbench from "../../features/detection/DamageFlowWorkbench";

const damageWorkspaceHighlights = [
  {
    label: "检测流程",
    value: "3 步",
    note: "上传照片、执行检测、生成病害档案"
  },
  {
    label: "结果结构",
    value: "已拆分",
    note: "列表、详情和任务面板按业务数据分区呈现"
  },
  {
    label: "档案联动",
    value: "已连接",
    note: "支持专家复核、处置记录和知识建议联动"
  }
];

function DamageWorkspacePage() {
  return (
    <div className="workspace-page damage-workspace-page">
      <WorkspaceHeader
        currentModuleId="damage"
        description="承接古建筑照片上传、病害检测、档案生成和详情复核。"
        eyebrow="病害上传与结果复核"
        status="已连接"
        title="图片检测"
      />

      <section className="panel workspace-highlight-panel">
        <div className="workspace-highlight-grid">
          {damageWorkspaceHighlights.map((item) => (
            <article className="workspace-highlight-card" key={item.label}>
              <span>{item.label}</span>
              <strong>{item.value}</strong>
              <p>{item.note}</p>
            </article>
          ))}
        </div>
      </section>

      <div className="damage-flow-page">
        <DamageFlowWorkbench />
      </div>
    </div>
  );
}

export default DamageWorkspacePage;
