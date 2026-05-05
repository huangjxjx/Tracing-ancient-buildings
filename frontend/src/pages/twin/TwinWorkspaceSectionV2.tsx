import { useEffect, useMemo, useState } from "react";

import { getTwinPage, type TwinPagePayload } from "../../api/twin";
import { TwinArchivePanelV2 } from "../../features/twin/TwinArchivePanelV2";
import { TwinSceneCanvasV2 } from "../../features/twin/TwinSceneCanvasV2";

export function TwinWorkspaceSectionV2() {
  const [twinData, setTwinData] = useState<TwinPagePayload | null>(null);
  const [loadState, setLoadState] = useState<"loading" | "ready" | "error">("loading");
  const [errorMessage, setErrorMessage] = useState("");
  const [selectedComponentId, setSelectedComponentId] = useState<string | null>(null);
  const [selectedDamageId, setSelectedDamageId] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    const loadTwinPage = async () => {
      try {
        const payload = await getTwinPage();
        if (cancelled) {
          return;
        }

        setTwinData(payload);
        setSelectedDamageId(payload.defaultDamageId);
        setLoadState("ready");
        setErrorMessage("");
      } catch (error) {
        if (cancelled) {
          return;
        }

        setTwinData(null);
        setSelectedDamageId(null);
        setLoadState("error");
        setErrorMessage(error instanceof Error ? error.message : "数字孪生数据加载失败");
      }
    };

    loadTwinPage();

    return () => {
      cancelled = true;
    };
  }, []);

  const data = twinData;

  const twinSignals = useMemo(
    () => [
      { icon: "SITE", label: "站点", value: data?.site.regionName ?? "--" },
      { icon: "NODE", label: "模型节点", value: `${data?.sceneNodes.length ?? 0}` },
      { icon: "COMP", label: "构件档案", value: `${data?.components.length ?? 0}` },
      { icon: "RISK", label: "病害点位", value: `${data?.damagePoints.length ?? 0}` }
    ],
    [data?.components.length, data?.damagePoints.length, data?.sceneNodes.length, data?.site.regionName]
  );

  useEffect(() => {
    if (!data) {
      return;
    }

    setSelectedComponentId(null);
    setSelectedDamageId(data.defaultDamageId);
  }, [data]);

  if (loadState === "loading" && !data) {
    return (
      <section className="panel twin-panel" id="twin">
        <div className="panel-heading">
          <div>
            <span className="section-tag">数字孪生</span>
            <h3>正在读取后端孪生数据</h3>
          </div>
          <span className="status-pill">加载中</span>
        </div>
        <p>系统正在读取场景节点、构件档案和病害点位坐标。</p>
      </section>
    );
  }

  if (!data) {
    return (
      <section className="panel twin-panel" id="twin">
        <div className="panel-heading">
          <div>
            <span className="section-tag">接口错误</span>
            <h3>数字孪生数据暂时无法加载</h3>
          </div>
          <span className="status-pill warm">需要检查后端</span>
        </div>
        <p>{errorMessage}</p>
      </section>
    );
  }

  const selectedDamage = data.damagePoints.find((item) => item.id === selectedDamageId) ?? null;
  const resolvedComponentId = selectedDamage?.componentId ?? selectedComponentId ?? data.components[0]?.id ?? null;

  const handleSelectComponent = (componentId: string) => {
    setSelectedComponentId(componentId);
    setSelectedDamageId(null);
  };

  const handleSelectDamage = (damageId: string) => {
    setSelectedDamageId(damageId);
    setSelectedComponentId(null);
  };

  return (
    <section className="panel twin-panel" id="twin">
      <div className="panel-heading">
        <div>
          <span className="section-tag">Three.js 数字孪生</span>
          <h3>{data.site.name} 三维场景</h3>
        </div>
        <span className="status-pill">后端数据驱动</span>
      </div>

      <p>
        当前场景由后端返回的构件节点、空间坐标和病害点位实时装配。点击塔身、屋面、柱组或风险热点，可同步切换右侧档案。
      </p>

      <div className="workspace-signal-grid twin-signal-grid">
        {twinSignals.map((item) => (
          <article className="workspace-signal-card twin-signal-card" key={item.label}>
            <span className="signal-icon" aria-hidden="true">
              {item.icon}
            </span>
            <div>
              <span>{item.label}</span>
              <strong>{item.value}</strong>
            </div>
          </article>
        ))}
      </div>

      <div className="twin-layout">
        <TwinSceneCanvasV2
          components={data.components}
          damagePoints={data.damagePoints}
          onSelectComponent={handleSelectComponent}
          onSelectDamage={handleSelectDamage}
          sceneNodes={data.sceneNodes}
          selectedComponentId={resolvedComponentId}
          selectedDamageId={selectedDamageId}
        />

        <TwinArchivePanelV2
          components={data.components}
          damagePoints={data.damagePoints}
          onSelectComponent={handleSelectComponent}
          onSelectDamage={handleSelectDamage}
          selectedComponentId={resolvedComponentId}
          selectedDamageId={selectedDamageId}
        />
      </div>
    </section>
  );
}
