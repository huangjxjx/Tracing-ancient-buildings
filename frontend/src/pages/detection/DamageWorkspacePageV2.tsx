import { useCallback, useEffect, useMemo, useState } from "react";

import {
  createDetectionBatch,
  deleteDetectionBatch,
  getDetectionBatch,
  getDetectionBatches,
  reviewDetectionResult,
  type DetectionBatchDetailPayload
} from "../../api/detection";
import { createUploadSession, getUploadedFileUrl, uploadFileToLocalStorage } from "../../api/uploads";
import {
  createWorkOrder,
  getWorkOrders,
  updateWorkOrderStatus,
  type WorkOrder,
  type WorkOrderStatus
} from "../../api/workorders";
import { WorkspaceHeader } from "../../components/layout/WorkspaceHeader";
import type { DamageSeverity, DetectionReviewStatus } from "../../types/detection";

function severityLabel(severity: DamageSeverity) {
  if (severity === "high") {
    return "高风险";
  }
  if (severity === "medium") {
    return "需复核";
  }
  return "轻微";
}

function statusText(status: DetectionBatchDetailPayload["status"]) {
  if (status === "queued") {
    return "等待后台任务";
  }
  if (status === "running") {
    return "正在检测";
  }
  if (status === "failed") {
    return "检测失败";
  }
  return "检测完成";
}

const reviewStatusLabel: Record<DetectionReviewStatus, string> = {
  pending: "待复核",
  approved: "已通过",
  rejected: "已驳回",
  needs_recheck: "需复查"
};

const workOrderStatusLabel: Record<WorkOrderStatus, string> = {
  candidate: "候选",
  created: "已创建",
  assigned: "已指派",
  in_progress: "处理中",
  done: "已完成"
};

function DamageWorkspacePageV2() {
  const [batch, setBatch] = useState<DetectionBatchDetailPayload | null>(null);
  const [batchHistory, setBatchHistory] = useState<DetectionBatchDetailPayload[]>([]);
  const [file, setFile] = useState<File | null>(null);
  const [buildingName, setBuildingName] = useState("应县木塔（佛宫寺释迦塔）");
  const [componentName, setComponentName] = useState("东南外槽柱组");
  const [message, setMessage] = useState("选择一张巡检照片开始。");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [historyBusy, setHistoryBusy] = useState(false);
  const [showAllHistory, setShowAllHistory] = useState(false);
  const [imageLoadFailed, setImageLoadFailed] = useState(false);
  const [selectedResultId, setSelectedResultId] = useState("");
  const [workOrders, setWorkOrders] = useState<WorkOrder[]>([]);
  const [flowBusy, setFlowBusy] = useState(false);
  const [flowMessage, setFlowMessage] = useState("");

  const completedCount = useMemo(() => batch?.tasks.filter((item) => item.status === "completed").length ?? 0, [batch]);
  const shouldPoll = batch?.status === "queued" || batch?.status === "running";
  const selectedResult = useMemo(
    () => batch?.results.find((item) => item.id === selectedResultId) ?? batch?.results[0],
    [batch, selectedResultId]
  );
  const selectedWorkOrder = useMemo(
    () => workOrders.find((item) => item.resultId === selectedResult?.id),
    [selectedResult?.id, workOrders]
  );
  const currentAssetUrl = batch && !imageLoadFailed ? getUploadedFileUrl(batch.asset.id) : "";
  const visibleHistory = showAllHistory ? batchHistory : batchHistory.slice(0, 4);
  const activeTask = batch?.tasks.find((item) => item.status === "running") ?? batch?.tasks.find((item) => item.status === "pending");

  const applyBatch = useCallback((nextBatch: DetectionBatchDetailPayload) => {
    setBatch(nextBatch);
    setImageLoadFailed(false);
    setSelectedResultId((current) => {
      if (nextBatch.results.some((item) => item.id === current)) {
        return current;
      }
      return nextBatch.results[0]?.id ?? "";
    });

    if (nextBatch.status === "completed") {
      setMessage(`检测完成，已生成 ${nextBatch.results.length} 条病害档案。`);
      setError("");
    } else if (nextBatch.status === "failed") {
      setMessage("检测失败，请检查上传文件或后端日志。");
      setError(nextBatch.errorMessage ?? "后台检测任务失败。");
    } else {
      setMessage(`${statusText(nextBatch.status)}，页面会自动刷新档案。`);
    }
  }, []);

  const refreshBatchHistory = useCallback(async () => {
    const payload = await getDetectionBatches(12);
    setBatchHistory(payload.items);
    return payload.items;
  }, []);

  const refreshWorkOrders = useCallback(async () => {
    const payload = await getWorkOrders();
    setWorkOrders(payload.items);
    return payload.items;
  }, []);

  const refreshBatch = useCallback(
    async (batchId: string) => {
      const nextBatch = await getDetectionBatch(batchId);
      applyBatch(nextBatch);
      return nextBatch;
    },
    [applyBatch]
  );

  const loadBatchById = useCallback(
    async (batchId: string) => {
      setHistoryBusy(true);
      setError("");
      try {
        const nextBatch = await refreshBatch(batchId);
        setMessage(`已切换到历史检测 ${nextBatch.batchId}。`);
      } catch (requestError) {
        setError(requestError instanceof Error ? requestError.message : "历史检测读取失败");
      } finally {
        setHistoryBusy(false);
      }
    },
    [refreshBatch]
  );

  const handleDeleteBatch = useCallback(
    async (batchId: string) => {
      setHistoryBusy(true);
      setError("");
      try {
        await deleteDetectionBatch(batchId);
        const nextHistory = await refreshBatchHistory();
        if (batch?.batchId === batchId) {
          const nextBatch = nextHistory[0];
          if (nextBatch) {
            applyBatch(nextBatch);
            setMessage(`已删除历史检测，当前切换到 ${nextBatch.batchId}。`);
          } else {
            setBatch(null);
            setSelectedResultId("");
            setMessage("已删除历史检测。当前暂无检测记录。");
          }
        } else {
          setMessage("已删除历史检测。");
        }
        await refreshWorkOrders();
      } catch (requestError) {
        setError(requestError instanceof Error ? requestError.message : "删除历史检测失败");
      } finally {
        setHistoryBusy(false);
      }
    },
    [applyBatch, batch?.batchId, refreshBatchHistory, refreshWorkOrders]
  );

  useEffect(() => {
    let cancelled = false;

    Promise.all([refreshBatchHistory(), refreshWorkOrders()])
      .then(([history]) => {
        if (cancelled) {
          return;
        }
        if (!history.length) {
          setMessage("还没有检测记录。上传照片后会创建第一条历史记录。");
          return;
        }
        applyBatch(history[0]);
        setMessage(`已恢复最近检测 ${history[0].batchId}，上传文件：${history[0].asset.name}。`);
      })
      .catch((requestError) => {
        if (!cancelled) {
          setMessage("还没有检测记录，或后端暂时不可用。");
          setError(requestError instanceof Error ? requestError.message : "");
        }
      });

    return () => {
      cancelled = true;
    };
  }, [applyBatch, refreshBatchHistory, refreshWorkOrders]);

  useEffect(() => {
    if (!batch || !shouldPoll) {
      return;
    }

    let cancelled = false;
    const timer = window.setInterval(() => {
      refreshBatch(batch.batchId)
        .then((nextBatch) => {
          if (!cancelled && (nextBatch.status === "completed" || nextBatch.status === "failed")) {
            refreshBatchHistory().catch(() => undefined);
            refreshWorkOrders().catch(() => undefined);
          }
        })
        .catch((requestError) => {
          if (!cancelled) {
            setError(requestError instanceof Error ? requestError.message : "刷新病害档案失败");
          }
        });
    }, 700);

    return () => {
      cancelled = true;
      window.clearInterval(timer);
    };
  }, [batch, refreshBatch, refreshBatchHistory, refreshWorkOrders, shouldPoll]);

  const handleCreateBatch = async () => {
    const normalizedBuildingName = buildingName.trim();
    const normalizedComponentName = componentName.trim();
    if (!file) {
      setError("请先选择一张照片。");
      return;
    }
    if (!normalizedBuildingName || !normalizedComponentName) {
      setError("请填写古建筑名称和照片对应的构件/区域。");
      return;
    }

    setBusy(true);
    setError("");
    setMessage("正在上传照片...");

    try {
      const session = await createUploadSession({
        filename: file.name,
        contentType: file.type || "application/octet-stream",
        bizType: "detection-image"
      });
      const uploadedAsset = await uploadFileToLocalStorage(session.uploadUrl, file);

      setMessage("照片已上传，正在创建检测任务...");
      const created = await createDetectionBatch({
        siteId: normalizedBuildingName,
        componentId: normalizedComponentName,
        assetIds: [uploadedAsset.assetId],
        source: "ground",
        capturedAt: new Date().toISOString()
      });

      await refreshBatch(created.batchId);
      await refreshBatchHistory();
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "上传或创建检测任务失败");
      setMessage("处理失败，请检查后端服务是否启动。");
    } finally {
      setBusy(false);
    }
  };

  const handleReview = async (reviewStatus: DetectionReviewStatus) => {
    if (!selectedResult || !batch) {
      return;
    }
    setFlowBusy(true);
    setFlowMessage("");
    try {
      await reviewDetectionResult(selectedResult.id, {
        reviewStatus,
        note: `local review: ${reviewStatus}`
      });
      await refreshBatch(batch.batchId);
      await refreshWorkOrders();
      await refreshBatchHistory();
      setFlowMessage(`复核状态已更新为 ${reviewStatusLabel[reviewStatus]}。`);
    } catch (requestError) {
      setFlowMessage(requestError instanceof Error ? requestError.message : "复核提交失败。");
    } finally {
      setFlowBusy(false);
    }
  };

  const handleCreateWorkOrder = async () => {
    if (!selectedResult || !batch) {
      return;
    }
    setFlowBusy(true);
    setFlowMessage("");
    try {
      const workOrder = await createWorkOrder({
        resultId: selectedResult.id,
        note: "created from local detection review"
      });
      await refreshWorkOrders();
      await refreshBatchHistory();
      await refreshBatch(batch.batchId);
      setFlowMessage(`处置任务 ${workOrder.workOrderId} 已创建。总览、知识、监管和数字档案页面会读取这条后端记录。`);
    } catch (requestError) {
      setFlowMessage(requestError instanceof Error ? requestError.message : "处置任务创建失败。");
    } finally {
      setFlowBusy(false);
    }
  };

  const handleAdvanceWorkOrder = async () => {
    if (!selectedWorkOrder || !batch) {
      return;
    }
    const nextStatusByStatus: Partial<Record<WorkOrderStatus, WorkOrderStatus>> = {
      candidate: "created",
      created: "assigned",
      assigned: "in_progress",
      in_progress: "done"
    };
    const nextStatus = nextStatusByStatus[selectedWorkOrder.status];
    if (!nextStatus) {
      return;
    }
    setFlowBusy(true);
    setFlowMessage("");
    try {
      const workOrder = await updateWorkOrderStatus(selectedWorkOrder.workOrderId, {
        status: nextStatus,
        note: `advance to ${nextStatus}`
      });
      await refreshWorkOrders();
      await refreshBatchHistory();
      await refreshBatch(batch.batchId);
      setFlowMessage(`处置任务状态已更新为 ${workOrderStatusLabel[workOrder.status]}。`);
    } catch (requestError) {
      setFlowMessage(requestError instanceof Error ? requestError.message : "处置任务状态更新失败。");
    } finally {
      setFlowBusy(false);
    }
  };

  return (
    <div className="page-stack">
      <WorkspaceHeader
        currentModuleId="damage"
        description="上传巡检照片，后端会完成病害检测，并把每条检测结果生成可追溯的病害档案。"
        eyebrow="操作"
        status={batch ? statusText(batch.status) : "等待上传"}
        title="图片检测与档案生成"
      />

      <section className="action-panel">
        <div>
          <h2>上传应县木塔巡检照片</h2>
          <p>检测完成后，每条结果都会写入病害档案，并同步到数字档案、处理知识和佛宫寺片区监管。</p>
        </div>
        <button className="btn primary" disabled={!file || busy || !buildingName.trim() || !componentName.trim()} onClick={handleCreateBatch} type="button">
          {busy ? "处理中..." : "上传并检测"}
        </button>
      </section>

      {error ? <div className="error-state">{error}</div> : null}

      <section className="main-grid">
        <div className="card">
          <div className="section-head">
            <div>
              <h2>选择照片</h2>
              <p>可上传木塔本体、台基、塔檐、外槽柱和彩画等巡检照片。</p>
            </div>
          </div>
          <div className="upload-box">
            <div className="grid grid-2">
              <label className="field-stack">
                <span>古建筑名称</span>
                <input
                  onChange={(event) => setBuildingName(event.target.value)}
                  placeholder="例如：应县木塔（佛宫寺释迦塔）"
                  type="text"
                  value={buildingName}
                />
              </label>
              <label className="field-stack">
                <span>构件 / 区域</span>
                <input
                  onChange={(event) => setComponentName(event.target.value)}
                  placeholder="例如：东南外槽柱组、上层塔檐、南侧台基"
                  type="text"
                  value={componentName}
                />
              </label>
            </div>
            <input
              accept="image/*"
              onChange={(event) => {
                setFile(event.target.files?.[0] ?? null);
                setError("");
              }}
              type="file"
            />
            <div className="row-between">
              <span className="muted">{file ? file.name : batch ? `当前检测图片：${batch.asset.name}` : "还未选择文件"}</span>
              <span className="status-chip">{file ? `${Math.round(file.size / 1024)} KB` : batch?.asset.statusLabel ?? "待选择"}</span>
            </div>
            {currentAssetUrl ? (
              <img
                alt={batch?.asset.name ?? "已上传图片"}
                className="upload-preview"
                onError={() => setImageLoadFailed(true)}
                src={currentAssetUrl}
              />
            ) : null}
            <p>{message}</p>
          </div>
        </div>

        <aside className="card">
          <div className="section-head">
            <div>
              <h2>检测历史</h2>
              <p>默认显示最近 4 条。</p>
            </div>
          </div>
          <div className="list">
            {batchHistory.length ? (
              visibleHistory.map((item) => (
                <div
                  className={`list-item history-button ${item.batchId === batch?.batchId ? "is-active" : ""}`}
                  key={item.batchId}
                >
                  <span className="step-number">{item.results.length}</span>
                  <div>
                    <div className="row-between">
                      <h3>{item.asset.name}</h3>
                      <span className={`status-chip ${item.status === "failed" ? "high" : ""}`}>{statusText(item.status)}</span>
                    </div>
                    <p>{item.siteId} / {item.componentId}</p>
                    <span className="metric-note">{item.batchId}</span>
                    <span className="metric-note">{item.createdAt}</span>
                    <div className="button-row history-actions">
                      <button className="btn ghost" disabled={historyBusy} onClick={() => loadBatchById(item.batchId)} type="button">
                        查看
                      </button>
                      <button className="btn ghost danger" disabled={historyBusy} onClick={() => handleDeleteBatch(item.batchId)} type="button">
                        删除
                      </button>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="empty-state">暂无历史。上传照片后会出现在这里。</div>
            )}
            {batchHistory.length > 4 ? (
              <button className="btn secondary" onClick={() => setShowAllHistory((current) => !current)} type="button">
                {showAllHistory ? "收起历史" : `查看更多 ${batchHistory.length - 4} 条`}
              </button>
            ) : null}
          </div>
        </aside>
      </section>

      {batch ? (
        <section className="compact-status">
          <div>
            <strong>{statusText(batch.status)}</strong>
            <span>
              {batch.progress}% / 任务 {completedCount}/{batch.tasks.length} / 档案 {batch.results.length}
            </span>
            <p>{activeTask ? `${activeTask.title}：${activeTask.description}` : "检测完成，病害档案已写入数字档案和知识页面。"}</p>
          </div>
          <div className="progress-track">
            <div className="progress-fill" style={{ width: `${batch.progress}%` }} />
          </div>
        </section>
      ) : (
        <div className="empty-state">暂无检测记录。先选择照片并点击“上传并检测”。</div>
      )}

      <section className="main-grid">
        <div className="card">
          <div className="section-head">
            <div>
              <h2>病害档案</h2>
              <p>每条检测结果都会作为档案进入数字档案页和知识页。</p>
            </div>
          </div>
          <div className="list">
            {batch?.results.length ? (
              batch.results.map((result, index) => (
                <div className="list-item" key={result.id}>
                  <span className="step-number">{index + 1}</span>
                  <div>
                    <div className="row-between">
                      <h3>{result.title || result.damageType || `病害档案 ${index + 1}`}</h3>
                      <span className={`status-chip ${result.severity}`}>{severityLabel(result.severity)}</span>
                    </div>
                    <p>{result.location} / 面积：{result.area || "待确认"}</p>
                    <span className="metric-note">置信度：{Math.round(result.confidence * 100)}%</span>
                    <span className="metric-note">来源：图像识别</span>
                    <span className="metric-note">复核：{reviewStatusLabel[result.reviewStatus]}</span>
                    <button className="btn ghost" onClick={() => setSelectedResultId(result.id)} type="button">
                      {selectedResult?.id === result.id ? "已选择" : "选择"}
                    </button>
                  </div>
                </div>
              ))
            ) : (
              <div className="empty-state">
                {shouldPoll ? "后台正在检测，完成后会自动生成档案。" : "暂无病害档案。"}
              </div>
            )}
          </div>
        </div>

        <aside className="card">
          <div className="section-head">
            <div>
              <h2>档案复核</h2>
              <p>复核通过后可继续转为现场处置任务；知识页会直接读取档案给出处理方法。</p>
            </div>
          </div>
          {selectedResult ? (
            <div className="step-list">
              <div className="step-item">
                <span className="step-number">1</span>
                <div>
                  <h3>{selectedResult.title}</h3>
                  <p>{selectedResult.summary}</p>
                  <span className="metric-note">建议：{selectedResult.suggestion}</span>
                </div>
              </div>
              <div className="step-item">
                <span className="step-number">2</span>
                <div>
                  <h3>当前档案状态</h3>
                  <p>
                    复核：{reviewStatusLabel[selectedResult.reviewStatus]}
                    {selectedWorkOrder ? ` / 处置任务：${workOrderStatusLabel[selectedWorkOrder.status]}` : " / 暂无处置任务"}
                  </p>
                  {flowMessage ? <span className="metric-note">{flowMessage}</span> : null}
                </div>
              </div>
              <div className="button-row">
                <button className="btn secondary" disabled={flowBusy} onClick={() => handleReview("approved")} type="button">
                  复核通过
                </button>
                <button className="btn ghost" disabled={flowBusy} onClick={() => handleReview("needs_recheck")} type="button">
                  需复查
                </button>
                <button
                  className="btn primary"
                  disabled={flowBusy || selectedResult.reviewStatus !== "approved" || Boolean(selectedWorkOrder)}
                  onClick={handleCreateWorkOrder}
                  type="button"
                >
                  {selectedWorkOrder ? "已有处置任务" : "转处置任务"}
                </button>
                {selectedWorkOrder ? (
                  <button
                    className="btn secondary"
                    disabled={flowBusy || selectedWorkOrder.status === "done"}
                    onClick={handleAdvanceWorkOrder}
                    type="button"
                  >
                    推进状态
                  </button>
                ) : null}
              </div>
            </div>
          ) : (
            <div className="empty-state">请选择一条病害档案。</div>
          )}
        </aside>
      </section>
    </div>
  );
}

export default DamageWorkspacePageV2;
