import { Link } from "react-router-dom";

import { routedWorkbenchModules, type RoutedWorkbenchId } from "../../data/workbenchRegistryData";

type WorkspaceHeaderProps = {
  currentModuleId: Exclude<RoutedWorkbenchId, "overview">;
  eyebrow?: string;
  title: string;
  description: string;
  status?: string;
};

export function WorkspaceHeader({
  currentModuleId,
  eyebrow = "功能页",
  title,
  description,
  status
}: WorkspaceHeaderProps) {
  const currentModule = routedWorkbenchModules.find((item) => item.id === currentModuleId);

  return (
    <header className="page-header">
      <div>
        <div className="breadcrumb">
          <Link to="/">工作台</Link>
          <span>/</span>
          <span>{currentModule?.shortLabel ?? title}</span>
        </div>
        <div className="title-row">
          <span className="eyebrow">{eyebrow}</span>
          <h1>{title}</h1>
          {status ? <span className="state-chip">{status}</span> : null}
        </div>
        <p>{description}</p>
      </div>
    </header>
  );
}
