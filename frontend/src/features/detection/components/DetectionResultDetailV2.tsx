import type { DetectionResult, DetectionReviewStatus } from "../../../types/detection";

type DetectionResultDetailV2Props = {
  canReview?: boolean;
  canCreateWorkOrder?: boolean;
  detailState?: "idle" | "loading" | "ready" | "error";
  isReviewing?: boolean;
  isCreatingWorkOrder?: boolean;
  onCreateWorkOrder?: () => void;
  onReviewResult?: (reviewStatus: DetectionReviewStatus) => void;
  result: DetectionResult | undefined;
  reviewMessage?: string;
  workOrderMessage?: string;
};

const severityLabelMap: Record<DetectionResult["severity"], string> = {
  high: "高风险",
  medium: "中风险",
  low: "低风险"
};

function DetectionResultDetailV2({
  canReview = false,
  canCreateWorkOrder = false,
  detailState = "idle",
  isReviewing = false,
  isCreatingWorkOrder = false,
  onCreateWorkOrder,
  onReviewResult,
  result,
  reviewMessage = "",
  workOrderMessage = ""
}: DetectionResultDetailV2Props) {
  if (!result) {
    return (
      <section className="panel result-detail-panel">
        <div className="panel-heading">
          <div>
            <span className="section-tag">结果详情</span>
            <h3>暂无检测结果</h3>
          </div>
        </div>
        <div className="result-detail-empty">
          <strong>还没有可查看的检测结果</strong>
          <p>创建并完成一个本地检测批次后，这里会展示结果详情和复核操作。</p>
        </div>
      </section>
    );
  }

  return (
    <section className="panel result-detail-panel">
      <div className="panel-heading">
        <div>
          <span className="section-tag">结果详情</span>
          <h3>{result.title}</h3>
        </div>
        <span className="status-pill">{result.reviewStatus}</span>
      </div>

      <div className="detail-hero">
        <div>
          <span className="detail-label">病害类型</span>
          <strong>{result.damageType}</strong>
        </div>
        <div>
          <span className="detail-label">风险等级</span>
          <strong>{severityLabelMap[result.severity]}</strong>
        </div>
      </div>

      <div className="detail-grid">
        <article className="detail-card">
          <span className="detail-label">置信度</span>
          <strong>{Math.round(result.confidence * 100)}%</strong>
          <p>模型版本：{result.modelVersion}</p>
        </article>
        <article className="detail-card">
          <span className="detail-label">面积</span>
          <strong>{result.area}</strong>
          <p>{result.boundingBox}</p>
        </article>
        <article className="detail-card">
          <span className="detail-label">构件位置</span>
          <strong>{result.component}</strong>
          <p>{result.location}</p>
        </article>
        <article className="detail-card">
          <span className="detail-label">修缮建议</span>
          <strong>建议</strong>
          <p>{result.suggestion}</p>
        </article>
      </div>

      <div className="detail-summary">
        <span className="detail-label">检测摘要</span>
        <p>{result.summary}</p>
      </div>

      <div className="detail-tags">
        {result.tags.map((tag) => (
          <span key={tag}>{tag}</span>
        ))}
      </div>

      {canReview ? (
        <div className="review-panel">
          <div>
            <span className="detail-label">人工复核</span>
            <strong>{detailState === "loading" ? "正在加载复核对象" : "更新真实结果的复核状态"}</strong>
            {reviewMessage ? <p>{reviewMessage}</p> : null}
            {workOrderMessage ? <p>{workOrderMessage}</p> : null}
          </div>
          <div className="review-actions">
            <button disabled={isReviewing} onClick={() => onReviewResult?.("approved")} type="button">
              复核通过
            </button>
            <button disabled={isReviewing} onClick={() => onReviewResult?.("needs_recheck")} type="button">
              需要复查
            </button>
            <button disabled={isReviewing} onClick={() => onReviewResult?.("rejected")} type="button">
              驳回结果
            </button>
            {canCreateWorkOrder ? (
              <button disabled={isCreatingWorkOrder} onClick={onCreateWorkOrder} type="button">
                {isCreatingWorkOrder ? "创建中..." : "创建工单"}
              </button>
            ) : null}
          </div>
        </div>
      ) : null}
    </section>
  );
}

export default DetectionResultDetailV2;
