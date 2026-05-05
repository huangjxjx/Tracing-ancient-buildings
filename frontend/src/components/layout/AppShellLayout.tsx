import { NavLink, Outlet } from "react-router-dom";

import { routedWorkbenchModules } from "../../data/workbenchRegistryData";

function resolveNavLinkClassName(isActive: boolean) {
  return `nav-link${isActive ? " is-active" : ""}`;
}

function AppShellLayout() {
  return (
    <div className="app-shell">
      <header className="shell-header">
        <div className="brand-block">
          <strong>巡迹古建</strong>
          <span>应县木塔巡检工作台</span>
        </div>

        <nav className="main-nav" aria-label="主导航">
          {routedWorkbenchModules.map((item) => (
            <NavLink
              className={({ isActive }) => resolveNavLinkClassName(isActive)}
              end={item.path === "/"}
              key={item.id}
              to={item.path}
            >
              {item.shortLabel}
            </NavLink>
          ))}
        </nav>
      </header>

      <main className="page-shell">
        <Outlet />
      </main>
    </div>
  );
}

export default AppShellLayout;
