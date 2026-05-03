(function () {
  let svgRoot = null;
  let overlayLayer = null;

  function initOverlaySystem() {
    const container = document.getElementById("svgContainer");

    const observer = new MutationObserver(() => {
      const svg = container.querySelector("svg");
      if (svg && svg !== svgRoot) {
        svgRoot = svg;
        setupOverlayLayer();
        attachCheckboxHandlers();
      }
    });

    observer.observe(container, { childList: true });
  }

  function setupOverlayLayer() {
    if (!svgRoot) return;

    const old = svgRoot.querySelector("#overlay-layer");
    if (old) old.remove();

    overlayLayer = document.createElementNS("http://www.w3.org/2000/svg", "g");
    overlayLayer.setAttribute("id", "overlay-layer");
    svgRoot.appendChild(overlayLayer);
  }

  function clearOverlay() {
    if (overlayLayer) overlayLayer.innerHTML = "";
  }

  function drawBands() {
    clearOverlay();

    const rects = [...svgRoot.querySelectorAll("rect")];
    if (rects.length === 0) return;

    const ys = rects.map(r => parseFloat(r.getAttribute("y")));
    const heights = rects.map(r => parseFloat(r.getAttribute("height")));

    const minY = Math.min(...ys);
    const maxY = Math.max(...ys.map((y, i) => y + heights[i]));
    const bandSize = (maxY - minY) / 5;

    for (let i = 0; i < 5; i++) {
      const y0 = minY + i * bandSize;

      const band = document.createElementNS("http://www.w3.org/2000/svg", "rect");
      band.setAttribute("x", 0);
      band.setAttribute("y", y0);
      band.setAttribute("width", "100%");
      band.setAttribute("height", bandSize);
      band.setAttribute("class", "overlay-band");

      overlayLayer.appendChild(band);
    }
  }

  function drawOrder() {
    clearOverlay();

    const rects = [...svgRoot.querySelectorAll("rect")];

    rects.forEach((r, i) => {
      const x = parseFloat(r.getAttribute("x"));
      const y = parseFloat(r.getAttribute("y"));

      const label = document.createElementNS("http://www.w3.org/2000/svg", "text");
      label.setAttribute("x", x + 4);
      label.setAttribute("y", y + 12);
      label.setAttribute("class", "overlay-order");
      label.textContent = i + 1;

      overlayLayer.appendChild(label);
    });
  }

  function drawInOut() {
    clearOverlay();

    // Only pick in/out points, not measurement points
    const points = [...svgRoot.querySelectorAll('circle[data-type]')];

    points.forEach(p => {
      const cx = parseFloat(p.getAttribute("cx"));
      const cy = parseFloat(p.getAttribute("cy"));
      const type = p.getAttribute("data-type"); // "in" or "out"

      const dot = document.createElementNS("http://www.w3.org/2000/svg", "circle");
      dot.setAttribute("cx", cx);
      dot.setAttribute("cy", cy);
      dot.setAttribute("r", 3);
      dot.setAttribute(
        "class",
        type === "in" ? "overlay-point-in" : "overlay-point-out"
      );

      overlayLayer.appendChild(dot);
    });
  }

  function drawMeasurement() {
    clearOverlay();

    // Measurement lines
    const lines = [...svgRoot.querySelectorAll('line[data-measure]')];
    lines.forEach(l => {
      const clone = l.cloneNode(true);
      clone.setAttribute("class", "overlay-measure-line");
      overlayLayer.appendChild(clone);
    });

    // Measurement points
    const circles = [...svgRoot.querySelectorAll('circle[data-measure]')];
    circles.forEach(c => {
      const clone = c.cloneNode(true);
      clone.setAttribute("class", "overlay-measure-point");
      overlayLayer.appendChild(clone);
    });
  }

  function attachCheckboxHandlers() {
    document.getElementById("show-bands").onchange = e => {
      if (e.target.checked) drawBands();
      else clearOverlay();
    };

    document.getElementById("show-order").onchange = e => {
      if (e.target.checked) drawOrder();
      else clearOverlay();
    };

    document.getElementById("show-inout").onchange = e => {
      if (e.target.checked) drawInOut();
      else clearOverlay();
    };

    document.getElementById("show-measure").onchange = e => {
      if (e.target.checked) drawMeasurement();
      else clearOverlay();
    };
  }

  initOverlaySystem();
})();
