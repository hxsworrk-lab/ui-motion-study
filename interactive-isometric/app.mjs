// Original study: local Three.js only. No remote assets, telemetry or client data.
const $ = (id) => document.getElementById(id);
const names = ['Request', 'Validate', 'Record', 'Confirm'];
const descriptions = [
  'A document marks the beginning of the illustrative route.',
  'A shield and check mark indicate a validation step. No real validation service is connected.',
  'Three stacked records represent recording information. No database is connected.',
  'A checked document marks the end of the illustrative sequence.'
];
const buttons = [...document.querySelectorAll('[data-step]')];
const motionQuery = matchMedia('(prefers-reduced-motion: reduce)');
let selected = 0;
let selectScene = null;
function selectStep(index, focus = false) {
  selected = ((index % 4) + 4) % 4;
  buttons.forEach((button, i) => button.setAttribute('aria-pressed', String(i === selected)));
  $('selected-number').textContent = `SELECTED / 0${selected + 1}`;
  $('selected-name').textContent = names[selected];
  $('selected-description').textContent = descriptions[selected];
  document.body.dataset.selected = String(selected);
  if (focus) buttons[selected].focus();
  selectScene?.();
}
buttons.forEach((button, index) => {
  button.addEventListener('click', () => selectStep(index));
  button.addEventListener('keydown', (event) => {
    const index = Number(button.dataset.step);
    if (['ArrowRight', 'ArrowDown', 'ArrowLeft', 'ArrowUp', 'Home', 'End'].includes(event.key)) {
      event.preventDefault();
      const next = event.key === 'Home' ? 0 : event.key === 'End' ? 3 : index + (['ArrowRight', 'ArrowDown'].includes(event.key) ? 1 : -1);
      selectStep(next, true);
    }
  });
});
$('world').addEventListener('keydown', (event) => {
  let next;
  if (/^[1-4]$/.test(event.key)) next = Number(event.key) - 1;
  if (event.key === 'ArrowRight') next = selected + 1;
  if (event.key === 'ArrowLeft') next = selected - 1;
  if (next !== undefined) { event.preventDefault(); selectStep(next); }
});
selectStep(0);

function fail(error) {
  console.error('Interactive study:', error);
  $('fallback').hidden = false;
  $('world').hidden = true;
  $('scene').dataset.failed = 'true';
  $('renderer-state').textContent = '3D unavailable · original vector still shown';
  $('geometry-state').textContent = 'ORIGINAL VECTOR STILL / STATIC FALLBACK';
  $('motion-state').textContent = 'Static fallback. Step descriptions remain available.';
  $('frame-samples').textContent = 'No live 3D measurement';
  $('play-toggle').disabled = true;
  document.body.dataset.ready = 'fallback';
}

try {
  const THREE = await import('./vendor/three.module.min.js');
  initialize(THREE);
} catch (error) { fail(error); }

function initialize(THREE) {
  const canvas = $('world');
  const host = $('scene');
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: false, powerPreference: 'high-performance' });
  renderer.setPixelRatio(Math.min(devicePixelRatio || 1, 1.75));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.setClearColor('#101d2b');
  const world = new THREE.Scene();
  const camera = new THREE.OrthographicCamera(-8, 8, 5, -5, .1, 100);
  world.add(new THREE.HemisphereLight(0xd9f4ff, 0x193145, 2.7));
  const light = new THREE.DirectionalLight(0xffffff, 3.1);
  light.position.set(-4, 9, 6); world.add(light);
  const root = new THREE.Group(); world.add(root);
  const material = (color, extra = {}) => new THREE.MeshStandardMaterial({ color, roughness: .8, metalness: .04, ...extra });
  const materials = {
    base: material('#192b3c'), body: material('#355267'), top: material('#c5e1df'),
    active: material('#77e8c4', { emissive: '#244f48', emissiveIntensity: .25 }),
    paper: material('#edf4f6'), folded: material('#9fb9c7'), check: material('#217a68'),
    ink: material('#526f82'), line: material('#34495e'), packet: material('#77e8c4', { emissive: '#77e8c4', emissiveIntensity: .35 })
  };
  const box = (parent, w, h, d, mat, x = 0, y = 0, z = 0) => {
    const mesh = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat);
    mesh.position.set(x, y, z); parent.add(mesh); return mesh;
  };
  const tube = (parent, points, radius, mat) => {
    const curve = new THREE.CurvePath();
    for (let i = 1; i < points.length; i++) curve.add(new THREE.LineCurve3(new THREE.Vector3(...points[i - 1]), new THREE.Vector3(...points[i])));
    const mesh = new THREE.Mesh(new THREE.TubeGeometry(curve, Math.max(8, points.length * 4), radius, 6, false), mat);
    parent.add(mesh); return mesh;
  };
  // A square in the ground plane projects into the source study's four-point diamond.
  const a = 2.95;
  const positions = [[-a, 0, a], [-a, 0, -a], [a, 0, -a], [a, 0, a]];
  const nodes = [];
  const pickables = [];
  const labelElements = [];
  positions.forEach((position, index) => {
    const group = new THREE.Group(); group.position.set(...position); root.add(group);
    box(group, 2.22, .15, 2.22, materials.base, 0, .025);
    box(group, 1.73, .35, 1.73, materials.body, 0, .26);
    const cap = box(group, 1.48, .09, 1.48, materials.top, 0, .48);
    const icon = new THREE.Group(); icon.rotation.y = Math.PI / 4; group.add(icon);
    if (index === 0 || index === 3) {
      box(icon, .67, .82, .09, materials.paper, 0, 1.02);
      box(icon, .16, .16, .025, materials.folded, .255, 1.35, .061);
      if (index === 0) {
        [0, 1, 2].forEach((i) => box(icon, [.32, .43, .25][i], .032, .035, materials.ink, -.025, 1.15 - i * .14, .063));
      } else {
        tube(icon, [[-.20, 1.02, .075], [-.055, .88, .075], [.23, 1.19, .075]], .035, materials.check);
      }
    } else if (index === 1) {
      const shape = new THREE.Shape();
      shape.moveTo(-.42, .25); shape.lineTo(0, .43); shape.lineTo(.42, .25);
      shape.lineTo(.34, -.18); shape.lineTo(0, -.48); shape.lineTo(-.34, -.18); shape.closePath();
      const shield = new THREE.Mesh(new THREE.ExtrudeGeometry(shape, { depth: .08, bevelEnabled: false }), materials.paper);
      shield.position.set(0, 1.08, -.035); icon.add(shield);
      tube(icon, [[-.22, 1.05, .075], [-.06, .89, .075], [.23, 1.22, .075]], .038, materials.check);
    } else {
      for (let i = 0; i < 3; i++) {
        const disk = new THREE.Mesh(new THREE.CylinderGeometry(.43, .43, .15, 28), materials.paper);
        disk.position.set(0, .72 + i * .24, 0); icon.add(disk);
      }
    }
    group.traverse((object) => { if (object.isMesh) { object.userData.nodeIndex = index; pickables.push(object); } });
    nodes.push({ group, cap });
    const label = document.createElement('div'); label.className = 'node-label';
    const num = document.createElement('span'); num.textContent = `0${index + 1}`;
    label.append(num, document.createTextNode(names[index])); $('labels').append(label); labelElements.push(label);
  });
  const route = positions.map(([x, , z]) => [x, .10, z]); route.push(route[0]);
  tube(root, route, .025, materials.line);
  const packet = new THREE.Mesh(new THREE.SphereGeometry(.12, 16, 10), materials.packet); root.add(packet);
  const raycaster = new THREE.Raycaster();
  const pointer = new THREE.Vector2();
  let down = null;
  canvas.addEventListener('pointerdown', (event) => { down = [event.clientX, event.clientY]; });
  canvas.addEventListener('pointerup', (event) => {
    if (!down || Math.hypot(event.clientX - down[0], event.clientY - down[1]) > 7) { down = null; return; }
    down = null;
    const rect = canvas.getBoundingClientRect();
    pointer.set((event.clientX - rect.left) / rect.width * 2 - 1, -(event.clientY - rect.top) / rect.height * 2 + 1);
    raycaster.setFromCamera(pointer, camera);
    const hit = raycaster.intersectObjects(pickables, false)[0];
    if (hit) selectStep(hit.object.userData.nodeIndex);
  });
  canvas.addEventListener('pointercancel', () => { down = null; });

  let reduced = motionQuery.matches;
  let running = !reduced;
  let phase = 0;
  let scrollProgress = 0;
  let scheduled = null;
  let previous = null;
  let previousFrame = null;
  let lastReport = 0;
  let draws = 0;
  let sampleCount = 0;
  const intervals = [];
  let firstDraw = null;
  let width = 1, height = 1;
  const projectPoint = new THREE.Vector3();
  function motionStatus() {
    $('play-toggle').disabled = reduced;
    $('play-toggle').textContent = reduced ? 'Motion reduced' : running ? 'Pause packet' : 'Play packet';
    $('play-toggle').setAttribute('aria-pressed', String(running));
    $('motion-state').textContent = reduced ? 'Reduced motion: static view; packet and scroll motion off.' : running ? 'Packet running · six-second loop' : 'Packet paused · scroll and selection remain available';
    document.body.dataset.reducedMotion = String(reduced);
    document.body.dataset.running = String(running);
    if (!running) $('frame-samples').textContent = reduced ? 'Static reduced-motion view · no continuous sampling' : 'Paused · no continuous sampling';
  }
  function requestDraw() { if (scheduled === null && !document.hidden) scheduled = requestAnimationFrame(draw); }
  function updateScroll() {
    const range = Math.max(1, document.documentElement.scrollHeight - innerHeight);
    scrollProgress = reduced ? 0 : Math.max(0, Math.min(1, scrollY / range));
    $('scroll-state').textContent = reduced ? 'Scroll motion off' : `Scroll angle: ${Math.round(scrollProgress * 100)}%`;
    requestDraw();
  }
  function resize() {
    width = Math.max(1, host.clientWidth); height = Math.max(1, host.clientHeight);
    renderer.setSize(width, height, false);
    const aspect = width / height;
    // Keep the entire square and all labels in view on both portrait and wide screens.
    const halfHeight = Math.max(5.0, 5.45 / aspect);
    camera.left = -halfHeight * aspect; camera.right = halfHeight * aspect;
    camera.top = halfHeight; camera.bottom = -halfHeight; camera.updateProjectionMatrix();
    updateScroll();
  }
  function draw(now) {
    scheduled = null;
    const delta = previous === null ? 0 : Math.min((now - previous) / 1000, .1);
    previous = now;
    if (running && !reduced) phase = (phase + delta) % 6;
    const edge = Math.floor(phase / 1.5) % 4;
    const amount = (phase % 1.5) / 1.5;
    const from = positions[edge], to = positions[(edge + 1) % 4];
    packet.position.set(from[0] + (to[0] - from[0]) * amount, .18, from[2] + (to[2] - from[2]) * amount);
    $('packet-state').textContent = `Packet route: ${names[edge]} → ${names[(edge + 1) % 4]}`;
    const angle = Math.PI / 4 + (reduced ? 0 : (scrollProgress - .5) * .21);
    camera.position.set(Math.cos(angle) * 13, 11 + scrollProgress * .6, Math.sin(angle) * 13);
    camera.lookAt(0, .3, 0);
    nodes.forEach(({ group, cap }, i) => {
      group.position.y = i === selected ? .10 : 0;
      cap.material = i === selected ? materials.active : materials.top;
      labelElements[i].classList.toggle('selected', i === selected);
    });
    renderer.render(world, camera); draws++;
    nodes.forEach(({ group }, i) => {
      projectPoint.set(group.position.x, -.43, group.position.z).project(camera);
      labelElements[i].style.left = `${(projectPoint.x + 1) * width / 2}px`;
      labelElements[i].style.top = `${(-projectPoint.y + 1) * height / 2}px`;
    });
    if (firstDraw === null) {
      firstDraw = performance.now();
      $('first-draw').textContent = `${firstDraw.toFixed(1)} ms from navigation start (render call returned)`;
      $('renderer-state').textContent = `${renderer.getContext().constructor.name.replace('RenderingContext', '')} · live 3D geometry`;
      $('scene-counts').textContent = `${renderer.info.memory.geometries} geometries · ${renderer.info.render.calls} draw calls · pixel ratio ${renderer.getPixelRatio().toFixed(2)}`;
      document.body.dataset.ready = 'webgl';
    }
    if (running && !reduced) {
      if (previousFrame !== null) {
        const interval = now - previousFrame;
        if (interval > 0) { intervals.push(interval); sampleCount++; if (intervals.length > 120) intervals.shift(); }
      }
      previousFrame = now;
      if (now - lastReport > 500 && intervals.length >= 12) {
        const sorted = [...intervals].sort((a, b) => a - b);
        const median = sorted[Math.floor(sorted.length / 2)];
        const p95 = sorted[Math.min(sorted.length - 1, Math.ceil(sorted.length * .95) - 1)];
        $('frame-samples').textContent = `Last ${sorted.length} intervals: median ${median.toFixed(1)} ms · p95 ${p95.toFixed(1)} ms (${sampleCount} sampled)`;
        lastReport = now;
      }
      requestDraw();
    } else previousFrame = null;
  }
  selectScene = requestDraw;
  $('play-toggle').addEventListener('click', () => {
    if (reduced) return;
    running = !running; previous = previousFrame = null; intervals.length = 0;
    motionStatus(); requestDraw();
  });
  motionQuery.addEventListener('change', (event) => {
    reduced = event.matches; running = !reduced;
    previous = previousFrame = null; intervals.length = 0;
    motionStatus(); updateScroll();
  });
  document.addEventListener('visibilitychange', () => {
    previous = previousFrame = null;
    if (document.hidden && scheduled !== null) { cancelAnimationFrame(scheduled); scheduled = null; }
    else requestDraw();
  });
  canvas.addEventListener('webglcontextlost', (event) => {
    event.preventDefault(); running = false;
    if (scheduled !== null) cancelAnimationFrame(scheduled);
    scheduled = null; fail(new Error('WebGL context lost'));
  });
  window.addEventListener('scroll', updateScroll, { passive: true });
  new ResizeObserver(resize).observe(host);
  window.addEventListener('resize', resize, { passive: true });
  // Read-only browser QA hook; it does not manufacture observations.
  window.studyDiagnostics = () => ({
    threeRevision: THREE.REVISION, renderer: renderer.getContext().constructor.name,
    selected, running, reducedMotion: reduced, scrollProgress, phaseSeconds: phase,
    firstRenderReturnMs: firstDraw, renderedFrames: draws, sampledIntervals: sampleCount,
    rollingIntervalsMs: [...intervals], geometries: renderer.info.memory.geometries,
    drawCalls: renderer.info.render.calls, viewport: { width, height },
    limit: 'CPU-side render return and rAF intervals; no GPU/paint or performance guarantee.'
  });
  motionStatus(); resize(); requestDraw();
}
