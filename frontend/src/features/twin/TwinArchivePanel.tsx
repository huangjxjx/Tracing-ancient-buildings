import type { TwinComponentRecord, TwinDamagePoint, TwinRiskLevel } from "./types";

type TwinArchivePanelProps = {
  components: TwinComponentRecord[];
  damagePoints: TwinDamagePoint[];
  selectedComponentId: string | null;
  selectedDamageId: string | null;
  onSelectComponent: (componentId: string) => void;
  onSelectDamage: (damageId: string) => void;
};

const riskLabelMap: Record<TwinRiskLevel, string> = {
  low: "I 级",
  medium: "II 级",
  high: "III 级"
};

function getRiskClassName(riskLevel: TwinRiskLevel) {
  return `risk-badge risk-${riskLevel}`;
}

export function TwinArchivePanel({
  components,
  damagePoints,
  selectedComponentId,
  selectedDamageId,
  onSelectComponent,
  onSelectDamage
}: TwinArchivePanelProps) {
  const selectedDamage = damagePoints.find((item) => item.id === selectedDamageId) ?? null;
  const resolvedComponentId = selectedDamage?.componentId ?? selectedComponentId ?? components[0]?.id ?? null;
  const selectedComponent = components.find((item) => item.id === resolvedComponentId) ?? null;
  const relatedDamageItems = damagePoints.filter((item) => item.componentId === selectedComponent?.id);

  return (
    <aside className="archive-board twin-archive-board">
      <div className="archive-panel-copy">
        <span className="section-tag">构件档案联动</span>
        <h4>{selectedDamage ? "病害档案" : "构件档案"}</h4>
        <p>
          {selectedDamage
            ? "点击病害点后展示病害详情，并同步定位所属构件。"
            : "点击构件或右侧列表，切换当前档案焦点与关联病害。"}
        </p>
      </div>

      {selectedComponent ? (
        <article className="archive-focus-card">
          <div className="archive-focus-head">
            <div>
              <span className="archive-focus-kicker">{selectedDamage ? selectedDamage.type : selectedComponent.category}</span>
              <strong>{selectedDamage ? selectedDamage.name : selectedComponent.name}</strong>
            </div>
            <span className={getRiskClassName(selectedDamage?.riskLevel ?? selectedComponent.riskLevel)}>
              {riskLabelMap[selectedDamage?.riskLevel ?? selectedComponent.riskLevel]}
            </span>
          </div>

          <p className="archive-focus-summary">
            {selectedDamage ? selectedDamage.description : selectedComponent.summary}
          </p>

          <div className="archive-focus-grid">
            {(selectedDamage
              ? [
                  { label: "所属构件", value: selectedComponent.name },
                  { label: "处理状态", value: selectedDamage.status },
                  { label: "病害评分", value: `${Math.round(selectedDamage.severityScore * 100)} / 100` },
                  { label: "最近复核", value: selectedDamage.inspectedAt }
                ]
              : [
                  { label: "材质", value: selectedComponent.material },
                  { label: "当前状态", value: selectedComponent.status },
                  { label: "最近巡检", value: selectedComponent.lastInspection },
                  { label: "关联病害", value: `${relatedDamageItems.length} 处` }
                ]
            ).map((item) => (
              <div className="archive-focus-metric" key={item.label}>
                <span>{item.label}</span>
                <strong>{item.value}</strong>
              </div>
            ))}
          </div>

          <div className="archive-action-note">
            <span>处置建议</span>
            <p>{selectedDamage ? selectedDamage.suggestion : selectedComponent.summary}</p>
          </div>
        </article>
      ) : null}

      {selectedComponent ? (
        <section className="archive-subsection">
          <div className="archive-subsection-head">
            <h5>关联病害</h5>
            <small>{relatedDamageItems.length ? "点击可回到点位" : "当前构件暂无病害"}</small>
          </div>
          <div className="archive-list archive-list-compact">
            {relatedDamageItems.length ? (
              relatedDamageItems.map((item) => (
                <button
                  className={`archive-item archive-item-button ${item.id === selectedDamageId ? "is-active" : ""}`}
                  key={item.id}
                  onClick={() => onSelectDamage(item.id)}
                  type="button"
                >
                  <div>
                    <strong>{item.name}</strong>
                    <p>{item.status}</p>
                  </div>
                  <div className="archive-meta">
                    <span>{Math.round(item.severityScore * 100)} 分</span>
                    <small>{item.type}</small>
                  </div>
                </button>
              ))
            ) : (
              <div className="archive-empty">当前焦点构件暂无关联病害点。</div>
            )}
          </div>
        </section>
      ) : null}

      <section className="archive-subsection">
        <div className="archive-subsection-head">
          <h5>构件目录</h5>
          <small>模拟后续真实构件树入口</small>
        </div>
        <div className="archive-list archive-list-compact">
          {components.map((component) => (
            <button
              className={`archive-item archive-item-button ${component.id === selectedComponent?.id && !selectedDamage ? "is-active" : ""}`}
              key={component.id}
              onClick={() => onSelectComponent(component.id)}
              type="button"
            >
              <div>
                <strong>{component.name}</strong>
                <p>{component.status}</p>
              </div>
              <div className="archive-meta">
                <span>{riskLabelMap[component.riskLevel]}</span>
                <small>{component.category}</small>
              </div>
            </button>
          ))}
        </div>
      </section>
    </aside>
  );
}
