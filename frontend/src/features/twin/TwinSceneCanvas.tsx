import { useEffect, useRef, useState } from "react";

import { loadThreeRuntime } from "./loadThreeRuntime";
import type { TwinComponentRecord, TwinDamagePoint, TwinSceneNode } from "./types";

type TwinSceneCanvasProps = {
  sceneNodes: TwinSceneNode[];
  components: TwinComponentRecord[];
  damagePoints: TwinDamagePoint[];
  selectedComponentId: string | null;
  selectedDamageId: string | null;
  onSelectComponent: (componentId: string) => void;
  onSelectDamage: (damageId: string) => void;
};

type TwinRuntimeState = {
  renderer: any;
  scene: any;
  camera: any;
  controls: any;
  raycaster: any;
  pointer: any;
  animationFrameId: number;
  resizeObserver: ResizeObserver | null;
  componentMeshes: Map<string, any[]>;
  damageGroups: Map<string, any>;
  damageMaterials: Map<string, any>;
  host: HTMLDivElement;
};

function resolveRiskTint(riskLevel: TwinDamagePoint["riskLevel"] | TwinComponentRecord["riskLevel"]) {
  switch (riskLevel) {
    case "high":
      return "#bf4b36";
    case "medium":
      return "#bf8a2a";
    default:
      return "#1f7a6f";
  }
}

function resolveSelectableTarget(object: any): { kind: "component" | "damage"; id: string } | null {
  let current = object;

  while (current) {
    if (current.userData?.selectKind && current.userData?.selectId) {
      return {
        kind: current.userData.selectKind,
        id: current.userData.selectId
      };
    }

    current = current.parent ?? null;
  }

  return null;
}

function createNodeMesh(THREE: any, node: TwinSceneNode) {
  let geometry: any;

  if (node.primitive === "box") {
    geometry = new THREE.BoxGeometry(...node.size);
  } else if (node.primitive === "cylinder") {
    geometry = new THREE.CylinderGeometry(
      node.radiusTop,
      node.radiusBottom,
      node.height,
      node.radialSegments ?? 32
    );
  } else {
    geometry = new THREE.CylinderGeometry(0, node.radius, node.height, node.radialSegments ?? 4);
  }

  const material = new THREE.MeshStandardMaterial({
    color: node.color,
    roughness: node.roughness ?? 0.8,
    metalness: node.metalness ?? 0.16
  });

  const mesh = new THREE.Mesh(geometry, material);
  mesh.position.set(...node.position);
  mesh.rotation.set(...(node.rotation ?? [0, 0, 0]));
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  mesh.userData.baseColor = node.color;

  const edges = new THREE.LineSegments(
    new THREE.EdgesGeometry(geometry),
    new THREE.LineBasicMaterial({
      color: node.wireColor ?? "#6c5540",
      transparent: true,
      opacity: 0.45
    })
  );
  edges.position.copy(mesh.position);
  edges.rotation.copy(mesh.rotation);

  return { mesh, edges };
}

function syncSelectionHighlight(
  runtime: TwinRuntimeState,
  components: TwinComponentRecord[],
  damagePoints: TwinDamagePoint[],
  selectedComponentId: string | null,
  selectedDamageId: string | null
) {
  const selectedDamage = damagePoints.find((item) => item.id === selectedDamageId) ?? null;
  const highlightedComponentId = selectedDamage?.componentId ?? selectedComponentId ?? null;
  const highlightedDamageIds = selectedDamage
    ? new Set([selectedDamage.id])
    : new Set(
        damagePoints
          .filter((item) => item.componentId === highlightedComponentId)
          .map((item) => item.id)
      );

  runtime.componentMeshes.forEach((meshes, componentId) => {
    const isActive = componentId === highlightedComponentId;
    const component = components.find((item) => item.id === componentId);
    const tint = resolveRiskTint(component?.riskLevel ?? "low");

    meshes.forEach((mesh) => {
      if (!mesh.material) {
        return;
      }

      mesh.material.color.set(mesh.userData.baseColor);
      mesh.material.emissive.set(isActive ? tint : "#000000");
      mesh.material.emissiveIntensity = isActive ? 0.22 : 0;
    });
  });

  runtime.damageGroups.forEach((group, damageId) => {
    const material = runtime.damageMaterials.get(damageId);
    const riskLevel = damagePoints.find((item) => item.id === damageId)?.riskLevel ?? "medium";
    const isActive = highlightedDamageIds.has(damageId);

    if (material) {
      material.color.set(resolveRiskTint(riskLevel));
      material.emissive.set(isActive ? "#fff3db" : "#2a120d");
      material.emissiveIntensity = isActive ? 0.7 : 0.35;
    }

    group.userData.isActive = isActive;
  });
}

export function TwinSceneCanvas({
  sceneNodes,
  components,
  damagePoints,
  selectedComponentId,
  selectedDamageId,
  onSelectComponent,
  onSelectDamage
}: TwinSceneCanvasProps) {
  const hostRef = useRef<HTMLDivElement | null>(null);
  const runtimeRef = useRef<TwinRuntimeState | null>(null);
  const onSelectComponentRef = useRef(onSelectComponent);
  const onSelectDamageRef = useRef(onSelectDamage);
  const [loadState, setLoadState] = useState<"loading" | "ready" | "error">("loading");

  useEffect(() => {
    onSelectComponentRef.current = onSelectComponent;
    onSelectDamageRef.current = onSelectDamage;
  }, [onSelectComponent, onSelectDamage]);

  useEffect(() => {
    const host = hostRef.current;

    if (!host) {
      return undefined;
    }

    let disposed = false;
    let detachEvents: (() => void) | undefined;

    const mountScene = async () => {
      setLoadState("loading");

      try {
        const { THREE, OrbitControls } = await loadThreeRuntime();

        if (disposed || !hostRef.current) {
          return;
        }

        const scene = new THREE.Scene();
        scene.fog = new THREE.Fog("#e6dcc9", 28, 54);

        const camera = new THREE.PerspectiveCamera(42, 1, 0.1, 120);
        camera.position.set(20, 14, 22);

        const renderer = new THREE.WebGLRenderer({
          antialias: true,
          alpha: true
        });
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        renderer.setSize(host.clientWidth, host.clientHeight);
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        host.innerHTML = "";
        host.appendChild(renderer.domElement);

        const controls = new OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.enablePan = false;
        controls.minDistance = 13;
        controls.maxDistance = 42;
        controls.minPolarAngle = Math.PI / 6;
        controls.maxPolarAngle = Math.PI / 2.05;
        controls.target.set(0, 4.8, 0);

        const raycaster = new THREE.Raycaster();
        const pointer = new THREE.Vector2();
        const componentMeshes = new Map<string, any[]>();
        const damageGroups = new Map<string, any>();
        const damageMaterials = new Map<string, any>();

        const ambientLight = new THREE.HemisphereLight("#fff4e7", "#bda688", 1.2);
        scene.add(ambientLight);

        const sunLight = new THREE.DirectionalLight("#fff0d8", 1.55);
        sunLight.position.set(16, 24, 12);
        sunLight.castShadow = true;
        sunLight.shadow.mapSize.set(1024, 1024);
        sunLight.shadow.camera.near = 1;
        sunLight.shadow.camera.far = 60;
        sunLight.shadow.camera.left = -20;
        sunLight.shadow.camera.right = 20;
        sunLight.shadow.camera.top = 20;
        sunLight.shadow.camera.bottom = -20;
        scene.add(sunLight);

        const fillLight = new THREE.PointLight("#1f7a6f", 0.45, 60);
        fillLight.position.set(-15, 8, -10);
        scene.add(fillLight);

        const gridHelper = new THREE.GridHelper(30, 24, "#c7a56c", "#d9cdb6");
        const gridMaterial = Array.isArray(gridHelper.material) ? gridHelper.material[0] : gridHelper.material;
        gridHelper.position.y = 0.01;
        gridMaterial.transparent = true;
        gridMaterial.opacity = 0.28;
        scene.add(gridHelper);

        const nodeComponentMap = new Map<string, string>();
        components.forEach((component) => {
          component.nodeIds.forEach((nodeId) => {
            nodeComponentMap.set(nodeId, component.id);
          });
        });

        sceneNodes.forEach((node) => {
          const { mesh, edges } = createNodeMesh(THREE, node);
          const componentId = nodeComponentMap.get(node.id);

          if (componentId) {
            mesh.userData.selectKind = "component";
            mesh.userData.selectId = componentId;
            edges.userData.selectKind = "component";
            edges.userData.selectId = componentId;
            componentMeshes.set(componentId, [...(componentMeshes.get(componentId) ?? []), mesh]);
          }

          scene.add(mesh);
          scene.add(edges);
        });

        damagePoints.forEach((damagePoint) => {
          const group = new THREE.Group();
          group.position.set(...damagePoint.position);
          group.userData.selectKind = "damage";
          group.userData.selectId = damagePoint.id;

          const sphereMaterial = new THREE.MeshStandardMaterial({
            color: resolveRiskTint(damagePoint.riskLevel),
            emissive: "#2a120d",
            emissiveIntensity: 0.35,
            metalness: 0.15,
            roughness: 0.32
          });

          const sphere = new THREE.Mesh(new THREE.SphereGeometry(0.38, 24, 24), sphereMaterial);
          sphere.castShadow = true;
          sphere.userData.selectKind = "damage";
          sphere.userData.selectId = damagePoint.id;
          group.add(sphere);

          const halo = new THREE.Mesh(
            new THREE.TorusGeometry(0.7, 0.06, 10, 36),
            new THREE.MeshBasicMaterial({
              color: resolveRiskTint(damagePoint.riskLevel),
              transparent: true,
              opacity: 0.56
            })
          );
          halo.rotation.x = Math.PI / 2;
          halo.userData.selectKind = "damage";
          halo.userData.selectId = damagePoint.id;
          group.add(halo);

          const stem = new THREE.Mesh(
            new THREE.CylinderGeometry(0.03, 0.03, 1.15, 8),
            new THREE.MeshBasicMaterial({
              color: resolveRiskTint(damagePoint.riskLevel),
              transparent: true,
              opacity: 0.58
            })
          );
          stem.position.y = -0.75;
          stem.userData.selectKind = "damage";
          stem.userData.selectId = damagePoint.id;
          group.add(stem);

          damageGroups.set(damagePoint.id, group);
          damageMaterials.set(damagePoint.id, sphereMaterial);
          scene.add(group);
        });

        const resize = () => {
          const width = host.clientWidth;
          const height = host.clientHeight;

          camera.aspect = width / Math.max(height, 1);
          camera.updateProjectionMatrix();
          renderer.setSize(width, height);
        };

        resize();

        const resizeObserver = new ResizeObserver(() => resize());
        resizeObserver.observe(host);

        let pointerDown = { x: 0, y: 0 };

        const updateCursor = (event: PointerEvent) => {
          const rect = renderer.domElement.getBoundingClientRect();
          pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
          pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
          raycaster.setFromCamera(pointer, camera);

          const target = raycaster
            .intersectObjects(scene.children, true)
            .map((entry: any) => resolveSelectableTarget(entry.object))
            .find(Boolean);

          renderer.domElement.style.cursor = target ? "pointer" : "grab";
        };

        const handlePointerDown = (event: PointerEvent) => {
          pointerDown = { x: event.clientX, y: event.clientY };
          renderer.domElement.style.cursor = "grabbing";
        };

        const handlePointerUp = (event: PointerEvent) => {
          const moved = Math.hypot(event.clientX - pointerDown.x, event.clientY - pointerDown.y);

          if (moved < 6) {
            const rect = renderer.domElement.getBoundingClientRect();
            pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
            pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
            raycaster.setFromCamera(pointer, camera);

            const hit = raycaster
              .intersectObjects(scene.children, true)
              .map((entry: any) => resolveSelectableTarget(entry.object))
              .find(Boolean);

            if (hit?.kind === "damage") {
              onSelectDamageRef.current(hit.id);
            } else if (hit?.kind === "component") {
              onSelectComponentRef.current(hit.id);
            }
          }

          renderer.domElement.style.cursor = "grab";
        };

        renderer.domElement.addEventListener("pointermove", updateCursor);
        renderer.domElement.addEventListener("pointerdown", handlePointerDown);
        renderer.domElement.addEventListener("pointerup", handlePointerUp);
        renderer.domElement.style.cursor = "grab";

        const animate = () => {
          controls.update();

          const t = performance.now() * 0.001;
          damageGroups.forEach((group) => {
            const pulse = 1 + Math.sin(t * 2.6 + group.position.x) * (group.userData.isActive ? 0.12 : 0.05);
            group.rotation.y = t * 0.5;
            group.scale.setScalar(pulse);
          });

          renderer.render(scene, camera);
          runtimeRef.current!.animationFrameId = window.requestAnimationFrame(animate);
        };

        runtimeRef.current = {
          renderer,
          scene,
          camera,
          controls,
          raycaster,
          pointer,
          animationFrameId: 0,
          resizeObserver,
          componentMeshes,
          damageGroups,
          damageMaterials,
          host
        };

        syncSelectionHighlight(runtimeRef.current, components, damagePoints, selectedComponentId, selectedDamageId);
        runtimeRef.current.animationFrameId = window.requestAnimationFrame(animate);
        setLoadState("ready");

        detachEvents = () => {
          renderer.domElement.removeEventListener("pointermove", updateCursor);
          renderer.domElement.removeEventListener("pointerdown", handlePointerDown);
          renderer.domElement.removeEventListener("pointerup", handlePointerUp);
        };
      } catch {
        if (!disposed) {
          setLoadState("error");
        }
      }
    };

    mountScene();

    return () => {
      disposed = true;
      detachEvents?.();

      const runtime = runtimeRef.current;
      if (!runtime) {
        return;
      }

      window.cancelAnimationFrame(runtime.animationFrameId);
      runtime.resizeObserver?.disconnect();
      runtime.controls.dispose();
      runtime.renderer.dispose();
      runtime.host.innerHTML = "";
      runtimeRef.current = null;
    };
  }, [components, damagePoints, sceneNodes]);

  useEffect(() => {
    if (!runtimeRef.current) {
      return;
    }

    syncSelectionHighlight(runtimeRef.current, components, damagePoints, selectedComponentId, selectedDamageId);
  }, [components, damagePoints, selectedComponentId, selectedDamageId]);

  return (
    <div className="twin-stage-shell">
      <div className="twin-stage-toolbar">
        <div className="twin-stage-copy">
          <span className="section-tag">Three.js 数字孪生</span>
          <strong>古建体块与病害点位演示场景</strong>
        </div>
        <div className="twin-stage-legend">
          <span>拖拽旋转</span>
          <span>滚轮缩放</span>
          <span>点击点位联动档案</span>
        </div>
      </div>

      <div className="twin-canvas-frame">
        <div className="twin-canvas-host" ref={hostRef} />
        {loadState !== "ready" ? (
          <div className="twin-stage-overlay">
            <strong>{loadState === "error" ? "Three.js 运行时加载失败" : "正在装配数字孪生场景"}</strong>
            <p>
              {loadState === "error"
                ? "当前实现依赖本地 three 包。若运行异常，请检查依赖安装和构建产物。"
                : "将加载地面、主体、屋面、柱体和可交互病害点。"}
            </p>
          </div>
        ) : null}
      </div>

      <div className="stage-caption twin-stage-caption">
        当前场景已按构件节点、病害点位和风险等级拆分，后续可以直接替换为真实模型节点和空间坐标。
      </div>
    </div>
  );
}
