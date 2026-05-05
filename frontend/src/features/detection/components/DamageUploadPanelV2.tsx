import type { DamageFlowScenario, LocalUploadState, UploadInstruction } from "../../../types/detection";

type DamageUploadPanelV2Props = {
  scenario: DamageFlowScenario;
  instructions: UploadInstruction[];
  selectedFile?: File | null;
  uploadState?: LocalUploadState;
  uploadMessage?: string;
  onFileChange?: (file: File | null) => void;
};

const uploadStateLabel: Record<LocalUploadState, string> = {
  idle: "等待上传",
  uploading: "上传中",
  uploaded: "已上传",
  error: "上传失败"
};

function DamageUploadPanelV2({
  scenario,
  instructions,
  selectedFile = null,
  uploadState = "idle",
  uploadMessage = "",
  onFileChange
}: DamageUploadPanelV2Props) {
  const progressStyle = { width: `${scenario.asset.progress}%` };

  return (
    <section className="panel damage-upload-panel">
      <div className="panel-heading">
        <div>
          <span className="section-tag">本地上传</span>
          <h3>上传检测图片并创建本地批次</h3>
        </div>
        <span className="status-pill">{uploadStateLabel[uploadState]}</span>
      </div>

      <div className={`upload-stage upload-stage-${scenario.id}`}>
        <div className="upload-stage-grid" />
        <div className="upload-stage-copy">
          <span>{scenario.queueSummary}</span>
          <strong>{selectedFile?.name ?? scenario.asset.name}</strong>
          <p>{uploadMessage || scenario.uploadHint}</p>
        </div>

        <div className="upload-progress-card">
          <div className="upload-progress-meta">
            <span>{selectedFile ? `${Math.round(selectedFile.size / 1024)} KB` : scenario.asset.source}</span>
            <strong>{scenario.asset.statusLabel}</strong>
          </div>
          <div className="upload-progress-track">
            <div className="upload-progress-fill" style={progressStyle} />
          </div>
          <small>采集时间：{scenario.asset.capturedAt}</small>
        </div>
      </div>

      <label className="upload-instruction-card" htmlFor="damage-local-upload">
        <strong>选择本地图片</strong>
        <p>{selectedFile ? selectedFile.name : "请选择一张本地图片，创建批次时会先上传到后端本地存储。"}</p>
        <input
          accept="image/*"
          id="damage-local-upload"
          onChange={(event) => onFileChange?.(event.target.files?.[0] ?? null)}
          type="file"
        />
      </label>

      <div className="upload-instruction-list">
        {instructions.map((item) => (
          <article className="upload-instruction-card" key={item.title}>
            <strong>{item.title}</strong>
            <p>{item.body}</p>
          </article>
        ))}
      </div>
    </section>
  );
}

export default DamageUploadPanelV2;
