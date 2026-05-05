import type { DetectionResult } from "../../../types/detection";

type DetectionResultListV2Props = {
  results: DetectionResult[];
  selectedResultId: string | null;
  onSelectResult: (resultId: string) => void;
};

const severityLabelMap: Record<DetectionResult["severity"], string> = {
  high: "高风险",
  medium: "中风险",
  low: "低风险"
};

function DetectionResultListV2({ results, selectedResultId, onSelectResult }: DetectionResultListV2Props) {
  return (
    <section className="panel result-list-panel">
      <div className="panel-heading">
        <div>
          <span className="section-tag">结果卡片</span>
          <h3>病害识别结果概览</h3>
        </div>
      </div>

      {results.length > 0 ? (
        <div className="result-list">
          {results.map((result) => (
            <button
              className={`result-card ${selectedResultId === result.id ? "result-card-active" : ""}`}
              key={result.id}
              onClick={() => onSelectResult(result.id)}
              type="button"
            >
              <div className="result-card-topline">
                <strong>{result.title}</strong>
                <span className={`severity-pill severity-pill-${result.severity}`}>{severityLabelMap[result.severity]}</span>
              </div>
              <p>{result.summary}</p>
              <div className="result-card-metrics">
                <span>置信度 {Math.round(result.confidence * 100)}%</span>
                <span>面积 {result.area}</span>
              </div>
              <small>{result.location}</small>
            </button>
          ))}
        </div>
      ) : (
        <div className="result-empty-state">
          <strong>结果待生成</strong>
          <p>当前状态下仅展示任务进度，识别完成后这里会返回病害候选结果列表。</p>
        </div>
      )}
    </section>
  );
}

export default DetectionResultListV2;
