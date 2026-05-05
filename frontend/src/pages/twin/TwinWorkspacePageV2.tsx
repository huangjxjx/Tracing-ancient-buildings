import { WorkspaceHeader } from "../../components/layout/WorkspaceHeader";

import { TwinWorkspaceSectionV2 } from "./TwinWorkspaceSectionV2";

function TwinWorkspacePageV2() {
  return (
    <div className="page-stack twin-page">
      <WorkspaceHeader
        currentModuleId="twin"
        description="展示可交互的 Three.js 古建筑数字孪生，支持构件级浏览、病害点定位、风险分级和档案联动。"
        eyebrow="空间场景"
        status="实时联动"
        title="古建筑数字孪生工作台"
      />

      <TwinWorkspaceSectionV2 />
    </div>
  );
}

export default TwinWorkspacePageV2;
