/**
 * Animated sine-wave background for the Fouriele player page.
 */
(function () {
  const svg = document.querySelector('.wave-background .wave-svg');
  if (!svg) return;

  const waves = [
    { y: 140, amplitude: 42, frequency: 0.012, phase: 0, speed: -0.7, stroke: 'rgba(148, 163, 184, 0.28)', width: 3 },
    { y: 320, amplitude: 36, frequency: 0.014, phase: 0.8, speed: 1.2, stroke: 'rgba(148, 163, 184, 0.22)', width: 3 },
    { y: 500, amplitude: 48, frequency: 0.011, phase: 1.6, speed: -1.6, stroke: 'rgba(148, 163, 184, 0.25)', width: 3 },
    { y: 660, amplitude: 32, frequency: 0.016, phase: 2.4, speed: 0.45, stroke: 'rgba(148, 163, 184, 0.18)', width: 2 },
  ];

  const paths = waves.map(function (cfg) {
    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    path.setAttribute('fill', 'none');
    path.setAttribute('stroke', cfg.stroke);
    path.setAttribute('stroke-width', String(cfg.width));
    path.setAttribute('stroke-linecap', 'round');
    svg.appendChild(path);
    return { el: path, cfg: cfg, phaseOffset: 0 };
  });

  function buildPath(cfg, phaseOffset) {
    const points = [];
    const step = 6;
    for (let x = -40; x <= 1240; x += step) {
      const y =
        cfg.y +
        Math.sin(x * cfg.frequency + cfg.phase + phaseOffset) * cfg.amplitude;
      points.push(x + ',' + y);
    }
    return 'M ' + points.join(' L ');
  }

  let lastTime = 0;

  function tick(time) {
    if (!lastTime) lastTime = time;
    const delta = (time - lastTime) / 1000;
    lastTime = time;

    paths.forEach(function (item) {
      item.phaseOffset += delta * (item.cfg.speed || 1);
      item.el.setAttribute('d', buildPath(item.cfg, item.phaseOffset));
    });

    requestAnimationFrame(tick);
  }

  paths.forEach(function (item) {
    item.el.setAttribute('d', buildPath(item.cfg, 0));
  });

  if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    requestAnimationFrame(tick);
  }
})();
