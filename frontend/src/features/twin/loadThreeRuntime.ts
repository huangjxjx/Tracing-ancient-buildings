export type ThreeRuntime = {
  THREE: any;
  OrbitControls: any;
};

let runtimePromise: Promise<ThreeRuntime> | null = null;

export function loadThreeRuntime(): Promise<ThreeRuntime> {
  if (!runtimePromise) {
    runtimePromise = Promise.all([
      import("three"),
      import("three/examples/jsm/controls/OrbitControls.js")
    ]).then(([THREE, controlsModule]) => ({
      THREE,
      OrbitControls: controlsModule.OrbitControls
    }));
  }

  return runtimePromise;
}
