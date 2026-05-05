import { Navigate, Route, Routes } from "react-router-dom";

import AppShellLayout from "./components/layout/AppShellLayout";
import DamageWorkspacePageV2 from "./pages/detection/DamageWorkspacePageV2";
import RepairKnowledgePageV2 from "./pages/knowledge/RepairKnowledgePageV2";
import OverviewPageV2 from "./pages/overview/OverviewPageV2";
import RegionalScreenPageV2 from "./pages/screen/RegionalScreenPageV2";
import TwinWorkspacePageV2 from "./pages/twin/TwinWorkspacePageV2";

function App() {
  return (
    <Routes>
      <Route element={<AppShellLayout />} path="/">
        <Route element={<OverviewPageV2 />} index />
        <Route element={<TwinWorkspacePageV2 />} path="twin-workspace" />
        <Route element={<DamageWorkspacePageV2 />} path="damage-workspace" />
        <Route element={<RepairKnowledgePageV2 />} path="repair-knowledge" />
        <Route element={<RegionalScreenPageV2 />} path="regional-screen" />
        <Route element={<Navigate replace to="/" />} path="*" />
      </Route>
    </Routes>
  );
}

export default App;
