export type TwinVector3 = [number, number, number];

export type TwinRiskLevel = "low" | "medium" | "high";

export type TwinSceneNode =
  | {
      id: string;
      label: string;
      primitive: "box";
      size: TwinVector3;
      position: TwinVector3;
      rotation?: TwinVector3;
      color: string;
      wireColor?: string;
      roughness?: number;
      metalness?: number;
    }
  | {
      id: string;
      label: string;
      primitive: "cylinder";
      radiusTop: number;
      radiusBottom: number;
      height: number;
      radialSegments?: number;
      position: TwinVector3;
      rotation?: TwinVector3;
      color: string;
      wireColor?: string;
      roughness?: number;
      metalness?: number;
    }
  | {
      id: string;
      label: string;
      primitive: "cone";
      radius: number;
      height: number;
      radialSegments?: number;
      position: TwinVector3;
      rotation?: TwinVector3;
      color: string;
      wireColor?: string;
      roughness?: number;
      metalness?: number;
    };

export type TwinMetric = {
  label: string;
  value: string;
};

export type TwinComponentRecord = {
  id: string;
  name: string;
  category: string;
  material: string;
  riskLevel: TwinRiskLevel;
  status: string;
  summary: string;
  lastInspection: string;
  nodeIds: string[];
  focusPoint: TwinVector3;
  metrics: TwinMetric[];
  relatedDamageIds: string[];
};

export type TwinDamagePoint = {
  id: string;
  name: string;
  componentId: string;
  type: string;
  riskLevel: TwinRiskLevel;
  severityScore: number;
  status: string;
  description: string;
  suggestion: string;
  position: TwinVector3;
  anchorNodeId: string;
  inspectedAt: string;
};

export type TwinSiteRecord = {
  id: string;
  name: string;
  regionName: string;
  sceneVersion: string;
  modelAssetKey?: string | null;
  coordinateReference: string;
};

export type TwinPagePayload = {
  site: TwinSiteRecord;
  sceneNodes: TwinSceneNode[];
  components: TwinComponentRecord[];
  damagePoints: TwinDamagePoint[];
  defaultDamageId: string | null;
};
