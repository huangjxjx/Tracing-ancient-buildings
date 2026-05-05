export type DamageFlowScenarioId = "idle" | "processing" | "completed";

export type DetectionTaskStatus = "pending" | "running" | "completed";

export type DamageSeverity = "high" | "medium" | "low";

export interface UploadInstruction {
  title: string;
  body: string;
}

export interface UploadAsset {
  id: string;
  name: string;
  source: string;
  capturedAt: string;
  progress: number;
  statusLabel: string;
}

export interface DetectionTask {
  id: string;
  title: string;
  description: string;
  status: DetectionTaskStatus;
  progress: number;
  eta: string;
}

export interface DetectionResult {
  id: string;
  taskId: string;
  title: string;
  damageType: string;
  confidence: number;
  area: string;
  severity: DamageSeverity;
  location: string;
  component: string;
  boundingBox: string;
  suggestion: string;
  summary: string;
  reviewStatus: string;
  modelVersion: string;
  tags: string[];
}

export interface DamageFlowScenario {
  id: DamageFlowScenarioId;
  label: string;
  helper: string;
  heroTitle: string;
  heroDescription: string;
  uploadHint: string;
  uploadBadge: string;
  queueSummary: string;
  asset: UploadAsset;
  tasks: DetectionTask[];
  results: DetectionResult[];
}

export const uploadInstructions: UploadInstruction[] = [
  {
    title: "建议文件来源",
    body: "支持无人机巡检图、单反近景图和移动端补拍图片，便于统一归入巡检批次。"
  },
  {
    title: "识别前置要求",
    body: "单张图片建议保留拍摄时间、机位和构件编号，便于进行位置确认与时序比对。"
  },
  {
    title: "结果复核提醒",
    body: "识别结果进入任务列表后，可继续完成人工复核、工单派发和数字孪生联动。"
  }
];

export const damageFlowScenarios: Record<DamageFlowScenarioId, DamageFlowScenario> = {
  idle: {
    id: "idle",
    label: "上传前",
    helper: "待提交",
    heroTitle: "等待创建病害识别任务",
    heroDescription: "当前批次尚未提交图像，请先确认拍摄批次、构件编号和病害巡检范围，再发起识别任务。",
    uploadHint: "拖拽病害图像到此处，系统将自动归入当前巡检批次。",
    uploadBadge: "待上传",
    queueSummary: "本批次尚未入队",
    asset: {
      id: "asset-idle",
      name: "未选择图像",
      source: "等待图像提交",
      capturedAt: "待上传",
      progress: 0,
      statusLabel: "等待用户提交"
    },
    tasks: [
      {
        id: "task-idle-1",
        title: "图像入库",
        description: "等待选择巡检批次和病害图像",
        status: "pending",
        progress: 0,
        eta: "--"
      },
      {
        id: "task-idle-2",
        title: "模型识别",
        description: "等待图像入库完成后触发",
        status: "pending",
        progress: 0,
        eta: "--"
      },
      {
        id: "task-idle-3",
        title: "结果归档",
        description: "等待识别结果映射到构件档案",
        status: "pending",
        progress: 0,
        eta: "--"
      }
    ],
    results: []
  },
  processing: {
    id: "processing",
    label: "识别中",
    helper: "分析进行中",
    heroTitle: "模型正在分析病害轮廓",
    heroDescription: "图像已入队并进入识别阶段，当前展示的是进度和任务链路，结果卡片将在推理完成后解锁。",
    uploadHint: "图像已完成提交，系统正在进行病害分析与结果整理。",
    uploadBadge: "识别中",
    queueSummary: "任务队列 3/4 已执行",
    asset: {
      id: "asset-processing",
      name: "IMG_EAST_BEAM_20260312_001.jpg",
      source: "东侧檐柱北立面 / 无人机补拍",
      capturedAt: "2026-03-12 09:24",
      progress: 68,
      statusLabel: "已上传，模型推理中"
    },
    tasks: [
      {
        id: "task-processing-1",
        title: "图像入库",
        description: "源文件已写入检测任务池",
        status: "completed",
        progress: 100,
        eta: "已完成"
      },
      {
        id: "task-processing-2",
        title: "病害识别",
        description: "正在执行裂缝、剥蚀和渗水联合检测",
        status: "running",
        progress: 68,
        eta: "约 18 秒"
      },
      {
        id: "task-processing-3",
        title: "结果归档",
        description: "等待模型输出后生成构件级摘要",
        status: "pending",
        progress: 0,
        eta: "等待中"
      }
    ],
    results: []
  },
  completed: {
    id: "completed",
    label: "识别完成",
    helper: "结果已生成",
    heroTitle: "本批次已生成 3 条病害识别结果",
    heroDescription: "结果卡片展示病害识别摘要，详情面板可查看风险等级、构件位置、修缮建议和复核状态。",
    uploadHint: "识别完成后可切换结果详情，并继续进行人工复核与处置流转。",
    uploadBadge: "已完成",
    queueSummary: "识别批次 XF-DET-20260312-03",
    asset: {
      id: "asset-completed",
      name: "IMG_EAST_BEAM_20260312_001.jpg",
      source: "东侧檐柱北立面 / 无人机补拍",
      capturedAt: "2026-03-12 09:24",
      progress: 100,
      statusLabel: "识别完成，等待复核"
    },
    tasks: [
      {
        id: "task-completed-1",
        title: "图像入库",
        description: "原始图像和巡检元数据已归档",
        status: "completed",
        progress: 100,
        eta: "已完成"
      },
      {
        id: "task-completed-2",
        title: "病害识别",
        description: "YOLO + 分割模型已输出病害候选区域",
        status: "completed",
        progress: 100,
        eta: "已完成"
      },
      {
        id: "task-completed-3",
        title: "结果归档",
        description: "结果已写入构件档案，等待专家复核",
        status: "completed",
        progress: 100,
        eta: "已完成"
      }
    ],
    results: [
      {
        id: "result-crack-east-column",
        taskId: "task-completed-2",
        title: "东侧檐柱纵向裂缝",
        damageType: "木构裂缝",
        confidence: 0.94,
        area: "0.36 m²",
        severity: "high",
        location: "东侧檐柱北立面 2.1m 至 2.8m",
        component: "东一檐柱 / 柱身",
        boundingBox: "x: 412, y: 188, w: 116, h: 284",
        suggestion: "先做含水率复核与裂缝活性监测，再决定是否采用可逆性灌注和表层加固。",
        summary: "裂缝沿木纹方向连续展开，疑似与长期受潮后的收缩变形有关。",
        reviewStatus: "待专家复核",
        modelVersion: "damage-detector-v0.9.2",
        tags: ["高风险", "需复测", "木构件"]
      },
      {
        id: "result-stone-flake-base",
        taskId: "task-completed-2",
        title: "台基表层剥蚀",
        damageType: "砖石剥蚀",
        confidence: 0.88,
        area: "1.12 m²",
        severity: "medium",
        location: "东侧台基转角外立面",
        component: "须弥座台基 / 东南角",
        boundingBox: "x: 108, y: 426, w: 208, h: 122",
        suggestion: "优先排查排水路径与返碱源头，再根据风化程度安排表层清理和局部补配。",
        summary: "病害区域边缘不规则，伴随轻微渗色，存在雨水冲刷叠加风化迹象。",
        reviewStatus: "已自动归类",
        modelVersion: "damage-detector-v0.9.2",
        tags: ["中风险", "砖石", "排水联动"]
      },
      {
        id: "result-paint-loss-beam",
        taskId: "task-completed-2",
        title: "额枋彩画褪色",
        damageType: "彩画褪色",
        confidence: 0.82,
        area: "0.22 m²",
        severity: "low",
        location: "正脊下方额枋中段",
        component: "前檐额枋 / 彩画层",
        boundingBox: "x: 286, y: 142, w: 94, h: 88",
        suggestion: "建议补采多光谱图像并复核色层病害范围，暂不直接进入修缮施工。",
        summary: "当前更接近表层颜料衰减，需结合光照和历史修缮记录进行二次判读。",
        reviewStatus: "建议补拍",
        modelVersion: "damage-detector-v0.9.2",
        tags: ["低风险", "彩画", "需补采"]
      }
    ]
  }
};

export const damageFlowScenarioOrder: DamageFlowScenarioId[] = ["idle", "processing", "completed"];
