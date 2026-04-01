const out = document.getElementById("output");

function log(msg) {
  out.textContent += msg + "\n";
}

function assert(cond, msg) {
  if (!cond) throw new Error("FAIL: " + msg);
  log("OK: " + msg);
}

log("Running viewer tests...");

// --- Test 1: parseSVG loads an SVG string ---
{
  const svgText = '<svg viewBox="0 0 10 10"><rect x="1" y="1" width="5" height="5"/></svg>';
  const el = parseSVG(svgText);

  assert(el instanceof SVGSVGElement, "parseSVG returns an SVG element");
  assert(el.querySelector("rect") !== null, "SVG contains a rect");
}

// --- Test 2: viewBox pan logic ---
{
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("viewBox", "0 0 100 100");

  const vb = svg.viewBox.baseVal;

  // simulate pan: move right 10, down 20
  vb.x += 10;
  vb.y += 20;

  assert(vb.x === 10, "viewBox.x updates on pan");
  assert(vb.y === 20, "viewBox.y updates on pan");
}

// --- Test 3: zoom logic ---
{
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("viewBox", "0 0 100 100");

  const vb = svg.viewBox.baseVal;

  // simulate zoom in (scale 0.9)
  vb.width *= 0.9;
  vb.height *= 0.9;

  assert(vb.width === 90, "zoom in reduces width");
  assert(vb.height === 90, "zoom in reduces height");
}

log("All tests passed.");
