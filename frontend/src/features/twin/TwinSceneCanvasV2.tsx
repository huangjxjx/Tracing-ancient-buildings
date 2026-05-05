import { useEffect, useRef, useState } from "react";

import { loadThreeRuntime } from "./loadThreeRuntime";
import type { TwinComponentRecord, TwinDamagePoint, TwinSceneNode } from "./types";

type TwinSceneCanvasV2Props = {
  sceneNodes: TwinSceneNode[];
  components: TwinComponentRecord[];
  damagePoints: TwinDamagePoint[];
  selectedComponentId: string | null;
  selectedDamageId: string | null;
  onSelectComponent: (componentId: string) => void;
  onSelectDamage: (damageId: string) => void;
};

type RuntimeState = {
  renderer: any;
  scene: any;
  camera: any;
  controls: any;
  raycaster: any;
  pointer: any;
  frameId: number;
  resizeObserver: ResizeObserver | null;
  componentMeshes: Map<string, any[]>;
  damageGroups: Map<string, any>;
  damageMaterials: Map<string, any>;
  host: HTMLDivElement;
};

function riskColor(riskLevel: TwinDamagePoint["riskLevel"] | TwinComponentRecord["riskLevel"]) {
  if (riskLevel === "high") {
    return "#b42318";
  }
  if (riskLevel === "medium") {
    return "#c58a2b";
  }
  return "#1f7a6f";
}

function resolveSelectableTarget(object: any): { kind: "component" | "damage"; id: string } | null {
  let current = object;
  while (current) {
    if (current.userData?.selectKind && current.userData?.selectId) {
      return { kind: current.userData.selectKind, id: current.userData.selectId };
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
    geometry = new THREE.CylinderGeometry(0, node.radius, node.height, node.radialSegments ?? 8);
  }

  const material = new THREE.MeshStandardMaterial({
    color: node.color,
    roughness: node.roughness ?? 0.78,
    metalness: node.metalness ?? 0.08
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
      color: node.wireColor ?? "#6f5a42",
      transparent: true,
      opacity: 0.34
    })
  );
  edges.position.copy(mesh.position);
  edges.rotation.copy(mesh.rotation);

  return { mesh, edges };
}

function syncSelection(
  runtime: RuntimeState,
  components: TwinComponentRecord[],
  damagePoints: TwinDamagePoint[],
  selectedComponentId: string | null,
  selectedDamageId: string | null
) {
  const selectedDamage = damagePoints.find((item) => item.id === selectedDamageId) ?? null;
  const activeComponentId = selectedDamage?.componentId ?? selectedComponentId ?? null;
  const activeDamageIds = selectedDamage
    ? new Set([selectedDamage.id])
    : new Set(damagePoints.filter((item) => item.componentId === activeComponentId).map((item) => item.id));

  runtime.componentMeshes.forEach((meshes, componentId) => {
    const component = components.find((item) => item.id === componentId);
    const active = componentId === activeComponentId;
    const tint = riskColor(component?.riskLevel ?? "low");

    meshes.forEach((mesh) => {
      mesh.material.color.set(mesh.userData.baseColor);
      mesh.material.emissive.set(active ? tint : "#000000");
      mesh.material.emissiveIntensity = active ? 0.18 : 0;
    });
  });

  runtime.damageGroups.forEach((group, damageId) => {
    const active = activeDamageIds.has(damageId);
    const damage = damagePoints.find((item) => item.id === damageId);
    const material = runtime.damageMaterials.get(damageId);

    group.userData.isActive = active;
    if (material && damage) {
      material.color.set(riskColor(damage.riskLevel));
      material.emissive.set(active ? "#fff0d0" : "#2a120d");
      material.emissiveIntensity = active ? 0.82 : 0.35;
    }
  });

  const focusPoint =
    selectedDamage?.position ?? components.find((item) => item.id === activeComponentId)?.focusPoint ?? null;

  if (focusPoint) {
    runtime.controls.target.set(focusPoint[0], focusPoint[1], focusPoint[2]);
  }
}

export function TwinSceneCanvasV2({
  sceneNodes,
  components,
  damagePoints,
  selectedComponentId,
  selectedDamageId,
  onSelectComponent,
  onSelectDamage
}: TwinSceneCanvasV2Props) {
  const hostRef = useRef<HTMLDivElement | null>(null);
  const runtimeRef = useRef<RuntimeState | null>(null);
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
        scene.fog = new THREE.Fog("#dfe7ea", 34, 72);

        const camera = new THREE.PerspectiveCamera(42, 1, 0.1, 160);
        camera.position.set(24, 18, 28);
        camera.lookAt(0, 7.2, 0);

        const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        renderer.setSize(host.clientWidth, host.clientHeight);
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        if ("outputColorSpace" in renderer) {
          renderer.outputColorSpace = THREE.SRGBColorSpace;
        }
        host.innerHTML = "";
        host.appendChild(renderer.domElement);

        const controls = new OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.enablePan = false;
        controls.minDistance = 9;
        controls.maxDistance = 52;
        controls.minPolarAngle = Math.PI / 8;
        controls.maxPolarAngle = Math.PI / 2.04;
        controls.target.set(0, 7.2, 0);

        scene.add(new THREE.HemisphereLight("#fff8ec", "#b3c2c8", 1.35));

        const sunLight = new THREE.DirectionalLight("#fff1dc", 1.85);
        sunLight.position.set(18, 30, 14);
        sunLight.castShadow = true;
        sunLight.shadow.mapSize.set(2048, 2048);
        sunLight.shadow.camera.near = 1;
        sunLight.shadow.camera.far = 80;
        sunLight.shadow.camera.left = -26;
        sunLight.shadow.camera.right = 26;
        sunLight.shadow.camera.top = 26;
        sunLight.shadow.camera.bottom = -26;
        scene.add(sunLight);

        const fillLight = new THREE.PointLight("#2c7a78", 0.55, 70);
        fillLight.position.set(-18, 10, -14);
        scene.add(fillLight);

        const ground = new THREE.Mesh(
          new THREE.CircleGeometry(22, 96),
          new THREE.MeshStandardMaterial({ color: "#d8c7a8", roughness: 0.95, metalness: 0.02 })
        );
        ground.rotation.x = -Math.PI / 2;
        ground.receiveShadow = true;
        scene.add(ground);

        const axisRing = new THREE.Mesh(
          new THREE.RingGeometry(8.8, 9.05, 96),
          new THREE.MeshBasicMaterial({
            color: "#7b9f98",
            transparent: true,
            opacity: 0.24,
            side: THREE.DoubleSide
          })
        );
        axisRing.rotation.x = -Math.PI / 2;
        axisRing.position.y = 0.04;
        scene.add(axisRing);

        const gridHelper = new THREE.GridHelper(36, 28, "#c7a56c", "#d9cdb6");
        const gridMaterial = Array.isArray(gridHelper.material) ? gridHelper.material[0] : gridHelper.material;
        gridHelper.position.y = 0.05;
        gridMaterial.transparent = true;
        gridMaterial.opacity = 0.24;
        scene.add(gridHelper);

        const raycaster = new THREE.Raycaster();
        const pointer = new THREE.Vector2();
        const componentMeshes = new Map<string, any[]>();
        const damageGroups = new Map<string, any>();
        const damageMaterials = new Map<string, any>();

        const nodeComponentMap = new Map<string, string>();
        components.forEach((component) => {
          component.nodeIds.forEach((nodeId) => nodeComponentMap.set(nodeId, component.id));
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
            color: riskColor(damagePoint.riskLevel),
            emissive: "#2a120d",
            emissiveIntensity: 0.35,
            metalness: 0.1,
            roughness: 0.28
          });

          const sphere = new THREE.Mesh(new THREE.SphereGeometry(0.34, 28, 28), sphereMaterial);
          sphere.castShadow = true;
          sphere.userData.selectKind = "damage";
          sphere.userData.selectId = damagePoint.id;
          group.add(sphere);

          const halo = new THREE.Mesh(
            new THREE.TorusGeometry(0.7, 0.055, 10, 42),
            new THREE.MeshBasicMaterial({
              color: riskColor(damagePoint.riskLevel),
              transparent: true,
              opacity: 0.58
            })
          );
          halo.rotation.x = Math.PI / 2;
          halo.userData.selectKind = "damage";
          halo.userData.selectId = damagePoint.id;
          group.add(halo);

          const stem = new THREE.Mesh(
            new THREE.CylinderGeometry(0.025, 0.025, 1.1, 8),
            new THREE.MeshBasicMaterial({
              color: riskColor(damagePoint.riskLevel),
              transparent: true,
              opacity: 0.62
            })
          );
          stem.position.y = -0.72;
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
        const resizeObserver = new ResizeObserver(resize);
        resizeObserver.observe(host);

        let pointerDown = { x: 0, y: 0 };

        const updatePointer = (event: PointerEvent) => {
          const rect = renderer.domElement.getBoundingClientRect();
          pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
          pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
          raycaster.setFromCamera(pointer, camera);
        };

        const updateCursor = (event: PointerEvent) => {
          updatePointer(event);
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
            updatePointer(event);
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

        runtimeRef.current = {
          renderer,
          scene,
          camera,
          controls,
          raycaster,
          pointer,
          frameId: 0,
          resizeObserver,
          componentMeshes,
          damageGroups,
          damageMaterials,
          host
        };

        syncSelection(runtimeRef.current, components, damagePoints, selectedComponentId, selectedDamageId);

        const animate = () => {
          controls.update();
          const t = performance.now() * 0.001;
          damageGroups.forEach((group) => {
            const pulse = 1 + Math.sin(t * 2.8 + group.position.x) * (group.userData.isActive ? 0.14 : 0.05);
            group.rotation.y = t * 0.7;
            group.scale.setScalar(pulse);
          });
          renderer.render(scene, camera);
          runtimeRef.current!.frameId = window.requestAnimationFrame(animate);
        };

        runtimeRef.current.frameId = window.requestAnimationFrame(animate);
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
      window.cancelAnimationFrame(runtime.frameId);
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
    syncSelection(runtimeRef.current, components, damagePoints, selectedComponentId, selectedDamageId);
  }, [components, damagePoints, selectedComponentId, selectedDamageId]);

  return (
    <div className="twin-stage-shell">
      <div className="twin-stage-toolbar">
        <div className="twin-stage-copy">
          <span className="section-tag">数字孪生场景</span>
          <strong>应县木塔构件级三维孪生</strong>
        </div>
        <div className="twin-stage-legend">
          <span>拖拽旋转</span>
          <span>滚轮缩放</span>
          <span>点击构件 / 热点联动档案</span>
        </div>
      </div>

      <div className="twin-canvas-frame">
        <div className="twin-canvas-host" ref={hostRef} />
        {loadState !== "ready" ? (
          <div className="twin-stage-overlay">
            <strong>{loadState === "error" ? "场景加载失败" : "正在加载数字孪生场景"}</strong>
            <p>
              {loadState === "error"
                ? "请确认前端依赖已安装，并刷新页面重试。"
                : "系统正在装配台基、塔身、檐层、柱组与病害点位。"}
            </p>
          </div>
        ) : null}
      </div>

      <div className="stage-caption twin-stage-caption">场景支持构件浏览、病害定位、风险分级和档案联动。</div>
    </div>
  );
}
