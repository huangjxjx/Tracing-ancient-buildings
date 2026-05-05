import { useEffect, useState } from "react";

import {
  createDetectionBatch,
  getDetectionBatch,
  getDetectionResult,
  getLatestDetectionBatch,
  mapDetectionBatchToScenario,
  reviewDetectionResult
} from "../../api/detection";
import { createUploadSession, uploadFileToLocalStorage } from "../../api/uploads";
import { createWorkOrder } from "../../api/workorders";
import type {
  DamageFlowScenario,
  DetectionResult,
  DetectionReviewStatus,
  LocalUploadState,
  UploadInstruction
} from "../../types/detection";
import DamageUploadPanelV2 from "./components/DamageUploadPanelV2";
import DetectionResultDetailV2 from "./components/DetectionResultDetailV2";
import DetectionResultListV2 from "./components/DetectionResultListV2";
import DetectionTaskListV2 from "./components/DetectionTaskListV2";
import "./damage-flow.css";

const emptyScenario: DamageFlowScenario = {
  id: "idle",
  label: "暂无批次",
  helper: "本地数据库中还没有真实检测批次",
  heroTitle: "暂无真实检测批次",
  heroDescription: "选择本地图片并创建检测批次后，系统会先上传文件，再用真实 assetId 创建批次。",
  uploadHint: "请选择一张本地图片。",
  uploadBadge: "等待上传",
  queueSummary: "未创建检测批次",
  asset: {
    id: "empty",
    name: "未选择文件",
    source: "本地检测",
    capturedAt: "--",
    progress: 0,
    statusLabel: "暂无上传"
  },
  tasks: [],
  results: []
};

const uploadInstructions: UploadInstruction[] = [
  {
    title: "真实上传",
    body: "创建批次前会调用后端上传接口，文件会写入 backend/storage/uploads。"
  },
  {
    title: "真实 assetId",
    body: "检测批次使用上传接口返回的 assetId，不再使用前端临时 mock asset。"
  },
  {
    title: "本地持久化",
    body: "上传记录和检测批次都会写入本地 SQLite 数据库。"
  }
];

function DamageFlowWorkbenchV2() {
  const [mode, setMode] = useState<"loading" | "api" | "empty" | "error">("loading");
  const [apiBatchId, setApiBatchId] = useState<string | null>(null);
  const [apiScenario, setApiScenario] = useState<DamageFlowScenario | null>(null);
  const [apiLoadState, setApiLoadState] = useState<"idle" | "loading" | "ready" | "error">("idle");
  const [apiErrorMessage, setApiErrorMessage] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadState, setUploadState] = useState<LocalUploadState>("idle");
  const [uploadMessage, setUploadMessage] = useState("");
  const [isCreatingBatch, setIsCreatingBatch] = useState(false);
  const [selectedResultId, setSelectedResultId] = useState<string | null>(null);
  const [selectedResultDetail, setSelectedResultDetail] = useState<DetectionResult | null>(null);
  const [resultDetailState, setResultDetailState] = useState<"idle" | "loading" | "ready" | "error">("idle");
  const [reviewState, setReviewState] = useState<"idle" | "loading" | "success" | "error">("idle");
  const [reviewMessage, setReviewMessage] = useState("");
  const [workOrderState, setWorkOrderState] = useState<"idle" | "loading" | "success" | "error">("idle");
  const [workOrderMessage, setWorkOrderMessage] = useState("");

  useEffect(() => {
    let cancelled = false;

    const bootstrapApiMode = async () => {
      setApiLoadState("loading");

      try {
        const payload = await getLatestDetectionBatch();
        if (cancelled) {
          return;
        }

        if (!payload) {
          setApiScenario(null);
          setApiBatchId(null);
          setMode("empty");
          setApiLoadState("ready");
          setApiErrorMessage("");
          return;
        }

        setApiScenario(mapDetectionBatchToScenario(payload));
        setApiBatchId(payload.batchId);
        setMode("api");
        setApiLoadState("ready");
        setApiErrorMessage("");
      } catch (error) {
        if (cancelled) {
          return;
        }

        setMode("error");
        setApiLoadState("error");
        setApiErrorMessage(error instanceof Error ? error.message : "检测批次加载失败");
      }
    };

    bootstrapApiMode();

    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (mode !== "api" || !apiBatchId) {
      return;
    }

    let cancelled = false;
    let pollTimeoutId: number | undefined;

    const loadBatch = async () => {
      setApiLoadState("loading");

      try {
        const payload = await getDetectionBatch(apiBatchId);
        if (cancelled) {
          return;
        }

        setApiScenario(mapDetectionBatchToScenario(payload));
        setApiLoadState("ready");
        setApiErrorMessage("");

        if (payload.status !== "completed") {
          pollTimeoutId = window.setTimeout(loadBatch, 3000);
        }
      } catch (error) {
        if (cancelled) {
          return;
        }

        setApiLoadState("error");
        setApiErrorMessage(error instanceof Error ? error.message : "检测批次刷新失败");
      }
    };

    loadBatch();

    return () => {
      cancelled = true;
      if (pollTimeoutId) {
        window.clearTimeout(pollTimeoutId);
      }
    };
  }, [apiBatchId, mode]);

  const activeScenario = apiScenario ?? emptyScenario;

  useEffect(() => {
    setSelectedResultId(activeScenario.results[0]?.id ?? null);
    setSelectedResultDetail(null);
    setResultDetailState("idle");
  }, [activeScenario]);

  useEffect(() => {
    if (mode !== "api" || !selectedResultId) {
      setSelectedResultDetail(null);
      setResultDetailState("idle");
      return;
    }

    let cancelled = false;

    const loadResultDetail = async () => {
      setResultDetailState("loading");

      try {
        const payload = await getDetectionResult(selectedResultId);
        if (cancelled) {
          return;
        }

        setSelectedResultDetail(payload);
        setResultDetailState("ready");
        setReviewMessage("");
        setWorkOrderMessage("");
      } catch (error) {
        if (cancelled) {
          return;
        }

        setSelectedResultDetail(null);
        setResultDetailState("error");
        setReviewMessage(error instanceof Error ? error.message : "检测结果详情加载失败");
      }
    };

    loadResultDetail();

    return () => {
      cancelled = true;
    };
  }, [mode, selectedResultId]);

  const selectedScenarioResult = activeScenario.results.find((item) => item.id === selectedResultId);
  const selectedResult = mode === "api" ? selectedResultDetail ?? selectedScenarioResult : selectedScenarioResult;
  const damageFlowSignals = [
    { label: "批次状态", value: activeScenario.label },
    { label: "结果数量", value: `${activeScenario.results.length}` },
    { label: "上传状态", value: uploadState === "uploaded" ? "已上传" : "本地文件" }
  ];

  const handleFileChange = (file: File | null) => {
    setSelectedFile(file);
    setUploadState("idle");
    setUploadMessage(file ? `已选择 ${file.name}` : "");
  };

  const handleCreateBatch = async () => {
    if (!selectedFile) {
      setUploadState("error");
      setUploadMessage("请先选择一张本地图片。");
      return;
    }

    setIsCreatingBatch(true);
    setUploadState("uploading");
    setUploadMessage("正在上传文件到本地后端存储...");

    try {
      const uploadSession = await createUploadSession({
        filename: selectedFile.name,
        contentType: selectedFile.type || "application/octet-stream",
        bizType: "detection-image"
      });
      const uploadedAsset = await uploadFileToLocalStorage(uploadSession.uploadUrl, selectedFile);
      setUploadState("uploaded");
      setUploadMessage(`文件已上传：${uploadedAsset.objectKey}`);

      const created = await createDetectionBatch({
        siteId: "site_001",
        componentId: "component-pillar-east",
        assetIds: [uploadedAsset.assetId],
        source: "ground",
        capturedAt: new Date().toISOString()
      });
      const payload = await getDetectionBatch(created.batchId);

      setMode("api");
      setApiBatchId(created.batchId);
      setApiScenario(mapDetectionBatchToScenario(payload));
      setApiErrorMessage("");
    } catch (error) {
      setMode("error");
      setUploadState("error");
      setUploadMessage(error instanceof Error ? error.message : "上传或创建批次失败");
      setApiErrorMessage(error instanceof Error ? error.message : "上传或创建批次失败");
    } finally {
      setIsCreatingBatch(false);
    }
  };

  const handleReviewResult = async (reviewStatus: DetectionReviewStatus) => {
    if (mode !== "api" || !selectedResultId || !apiBatchId) {
      return;
    }

    setReviewState("loading");

    try {
      const updatedResult = await reviewDetectionResult(selectedResultId, {
        reviewStatus,
        note: `本地复核：${reviewStatus}`
      });
      const refreshedBatch = await getDetectionBatch(apiBatchId);

      setSelectedResultDetail(updatedResult);
      setApiScenario(mapDetectionBatchToScenario(refreshedBatch));
      setSelectedResultId(updatedResult.id);
      setReviewState("success");
      setReviewMessage(`复核状态已更新为 ${reviewStatus}`);
      setWorkOrderMessage("");
    } catch (error) {
      setReviewState("error");
      setReviewMessage(error instanceof Error ? error.message : "复核提交失败");
    }
  };

  const handleCreateWorkOrder = async () => {
    if (mode !== "api" || !selectedResultId) {
      return;
    }

    setWorkOrderState("loading");

    try {
      const workOrder = await createWorkOrder({
        resultId: selectedResultId,
        note: "由本地检测结果创建"
      });
      setWorkOrderState("success");
      setWorkOrderMessage(`${workOrder.workOrderId} 已创建，负责人：${workOrder.ownerTeam}`);
    } catch (error) {
      setWorkOrderState("error");
      setWorkOrderMessage(error instanceof Error ? error.message : "工单创建失败");
    }
  };

  if (mode === "loading") {
    return (
      <section className="panel">
        <div className="panel-heading">
          <div>
            <span className="section-tag">病害检测</span>
            <h3>正在读取本地检测批次</h3>
          </div>
          <span className="status-pill">加载中</span>
        </div>
        <p>系统正在通过后端接口读取本地数据库中的最近检测批次。</p>
      </section>
    );
  }

  return (
    <div className="damage-flow-layout">
      <div className="workspace-signal-grid">
        {damageFlowSignals.map((item) => (
          <article className="workspace-signal-card" key={item.label}>
            <span>{item.label}</span>
            <strong>{item.value}</strong>
          </article>
        ))}
      </div>

      {mode === "error" || apiLoadState === "error" ? (
        <section className="panel">
          <div className="panel-heading">
            <div>
              <span className="section-tag">接口错误</span>
              <h3>检测批次暂时无法加载</h3>
            </div>
            <span className="status-pill warm">需要检查后端</span>
          </div>
          <p>{apiErrorMessage}</p>
        </section>
      ) : null}

      <section className="panel damage-flow-hero">
        <div className="damage-flow-hero-copy">
          <span className="section-tag">本地真实检测链路</span>
          <h2>{activeScenario.heroTitle}</h2>
          <p>{activeScenario.heroDescription}</p>
        </div>

        <div className="scenario-switcher">
          {apiBatchId ? (
            <div className="scenario-chip scenario-chip-active">
              <strong>{apiBatchId}</strong>
              <span>{activeScenario.helper}</span>
            </div>
          ) : null}

          <button className="scenario-chip" disabled={isCreatingBatch} onClick={handleCreateBatch} type="button">
            <strong>{isCreatingBatch ? "处理中..." : "上传并创建批次"}</strong>
            <span>{selectedFile ? selectedFile.name : "先选择本地图片"}</span>
          </button>
        </div>
      </section>

      <div className="damage-flow-grid">
        <div className="damage-flow-main">
          <DamageUploadPanelV2
            instructions={uploadInstructions}
            onFileChange={handleFileChange}
            scenario={activeScenario}
            selectedFile={selectedFile}
            uploadMessage={uploadMessage}
            uploadState={uploadState}
          />
          <DetectionTaskListV2 tasks={activeScenario.tasks} />
        </div>

        <div className="damage-flow-side">
          <DetectionResultListV2
            onSelectResult={setSelectedResultId}
            results={activeScenario.results}
            selectedResultId={selectedResultId}
          />
          <DetectionResultDetailV2
            canCreateWorkOrder={mode === "api" && selectedResult?.reviewStatus === "approved"}
            canReview={mode === "api" && Boolean(selectedResult)}
            detailState={resultDetailState}
            isCreatingWorkOrder={workOrderState === "loading"}
            isReviewing={reviewState === "loading"}
            onCreateWorkOrder={handleCreateWorkOrder}
            onReviewResult={handleReviewResult}
            result={selectedResult}
            reviewMessage={reviewMessage}
            workOrderMessage={workOrderMessage}
          />
        </div>
      </div>
    </div>
  );
}

export default DamageFlowWorkbenchV2;
