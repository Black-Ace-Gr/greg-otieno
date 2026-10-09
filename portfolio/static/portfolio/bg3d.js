/* Slow-moving 3D network with a wireframe core. Subtle, pauses when hidden, honours reduced motion. */
(function () {
  var canvas = document.getElementById("bg3d");
  if (!canvas || !window.THREE) return;
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var renderer;
  try {
    renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true, antialias: true });
  } catch (e) { return; }
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.75));

  var scene = new THREE.Scene();
  var camera = new THREE.PerspectiveCamera(60, 1, 0.1, 300);
  camera.position.z = 50;
  var group = new THREE.Group();
  scene.add(group);

  var small = window.innerWidth < 700;
  var N = small ? 70 : 140, LINK = small ? 10 : 11.5;
  var BX = 62, BY = 40, BZ = 28;
  var pos = new Float32Array(N * 3), vel = new Float32Array(N * 3);
  for (var i = 0; i < N; i++) {
    pos[i * 3] = (Math.random() - 0.5) * 2 * BX;
    pos[i * 3 + 1] = (Math.random() - 0.5) * 2 * BY;
    pos[i * 3 + 2] = (Math.random() - 0.5) * 2 * BZ;
    vel[i * 3] = (Math.random() - 0.5) * 0.035;
    vel[i * 3 + 1] = (Math.random() - 0.5) * 0.035;
    vel[i * 3 + 2] = (Math.random() - 0.5) * 0.035;
  }
  var pGeo = new THREE.BufferGeometry();
  var pAttr = new THREE.BufferAttribute(pos, 3);
  pAttr.setUsage(THREE.DynamicDrawUsage);
  pGeo.setAttribute("position", pAttr);
  var pMat = new THREE.PointsMaterial({ size: 0.8, transparent: true, opacity: 0.85, sizeAttenuation: true });
  group.add(new THREE.Points(pGeo, pMat));

  var MAXSEG = N * 6;
  var lPos = new Float32Array(MAXSEG * 6);
  var lGeo = new THREE.BufferGeometry();
  var lAttr = new THREE.BufferAttribute(lPos, 3);
  lAttr.setUsage(THREE.DynamicDrawUsage);
  lGeo.setAttribute("position", lAttr);
  lGeo.setDrawRange(0, 0);
  var lMat = new THREE.LineBasicMaterial({ transparent: true, opacity: 0.24 });
  group.add(new THREE.LineSegments(lGeo, lMat));

  var coreMat = new THREE.MeshBasicMaterial({ wireframe: true, transparent: true, opacity: 0.16 });
  var core = new THREE.Mesh(new THREE.IcosahedronGeometry(15, 1), coreMat);
  core.position.set(small ? 0 : 30, small ? 14 : 2, -10);
  group.add(core);

  function applyColor() {
    var c = getComputedStyle(document.documentElement).getPropertyValue("--accent").trim() || "#2447c8";
    var col = new THREE.Color(c);
    pMat.color.copy(col); lMat.color.copy(col); coreMat.color.copy(col);
  }
  applyColor();
  var mq = window.matchMedia("(prefers-color-scheme: dark)");
  if (mq.addEventListener) mq.addEventListener("change", function () { applyColor(); draw(); });

  function updateLinks() {
    var n = 0, l2 = LINK * LINK;
    for (var a = 0; a < N && n < MAXSEG; a++) {
      for (var b = a + 1; b < N && n < MAXSEG; b++) {
        var dx = pos[a * 3] - pos[b * 3], dy = pos[a * 3 + 1] - pos[b * 3 + 1], dz = pos[a * 3 + 2] - pos[b * 3 + 2];
        if (dx * dx + dy * dy + dz * dz < l2) {
          lPos.set([pos[a * 3], pos[a * 3 + 1], pos[a * 3 + 2], pos[b * 3], pos[b * 3 + 1], pos[b * 3 + 2]], n * 6);
          n++;
        }
      }
    }
    lGeo.setDrawRange(0, n * 2);
    lAttr.needsUpdate = true;
  }

  function step() {
    for (var i = 0; i < N; i++) {
      pos[i * 3] += vel[i * 3]; pos[i * 3 + 1] += vel[i * 3 + 1]; pos[i * 3 + 2] += vel[i * 3 + 2];
      if (Math.abs(pos[i * 3]) > BX) vel[i * 3] *= -1;
      if (Math.abs(pos[i * 3 + 1]) > BY) vel[i * 3 + 1] *= -1;
      if (Math.abs(pos[i * 3 + 2]) > BZ) vel[i * 3 + 2] *= -1;
    }
    pAttr.needsUpdate = true;
  }

  var mx = 0, my = 0, t = 0;
  window.addEventListener("pointermove", function (e) {
    mx = e.clientX / window.innerWidth - 0.5;
    my = e.clientY / window.innerHeight - 0.5;
  }, { passive: true });

  function draw() {
    updateLinks();
    var sy = window.scrollY || 0;
    group.rotation.y += (t * 0.00006 + mx * 0.35 - group.rotation.y) * 0.04;
    group.rotation.x += (my * 0.2 - group.rotation.x) * 0.04;
    camera.position.y = -Math.min(sy * 0.004, 8);
    core.rotation.x = t * 0.0003; core.rotation.y = t * 0.0004;
    renderer.render(scene, camera);
  }

  function resize() {
    var w = window.innerWidth, h = window.innerHeight;
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    draw();
  }
  window.addEventListener("resize", resize);
  resize();
  if (reduce) return; // single still frame

  var raf;
  function loop(now) {
    t = now; step(); draw();
    raf = requestAnimationFrame(loop);
  }
  raf = requestAnimationFrame(loop);
  document.addEventListener("visibilitychange", function () {
    if (document.hidden) cancelAnimationFrame(raf); else raf = requestAnimationFrame(loop);
  });
})();
