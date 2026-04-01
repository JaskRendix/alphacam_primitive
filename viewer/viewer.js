// --- Public helper for tests ---
function parseSVG(text) {
  const div = document.createElement("div");
  div.innerHTML = text.trim();
  return div.querySelector("svg");
}

// Expose for browser tests
window.parseSVG = parseSVG;


// --- Viewer logic ---
const fileInput = document.getElementById("fileInput");
const container = document.getElementById("svgContainer");

fileInput.addEventListener("change", async (e) => {
  const file = e.target.files[0];
  if (!file) return;

  const text = await file.text();
  container.innerHTML = text;

  const svg = container.querySelector("svg");
  if (!svg) return;

  enablePanZoom(svg);
});


function enablePanZoom(svg) {
  let isPanning = false;
  let startX = 0;
  let startY = 0;
  let viewBox = svg.viewBox.baseVal;

  // If the SVG has no viewBox, create one
  if (!svg.hasAttribute("viewBox")) {
    const width = svg.width.baseVal.value || 100;
    const height = svg.height.baseVal.value || 100;
    svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
    viewBox = svg.viewBox.baseVal;
  }

  svg.addEventListener("mousedown", (e) => {
    isPanning = true;
    startX = e.clientX;
    startY = e.clientY;
    svg.style.cursor = "grabbing";
  });

  svg.addEventListener("mousemove", (e) => {
    if (!isPanning) return;

    const dx = startX - e.clientX;
    const dy = startY - e.clientY;

    viewBox.x += dx;
    viewBox.y += dy;

    startX = e.clientX;
    startY = e.clientY;
  });

  svg.addEventListener("mouseup", () => {
    isPanning = false;
    svg.style.cursor = "grab";
  });

  svg.addEventListener("mouseleave", () => {
    isPanning = false;
    svg.style.cursor = "grab";
  });

  svg.addEventListener("wheel", (e) => {
    e.preventDefault();

    const scale = e.deltaY > 0 ? 1.1 : 0.9;
    viewBox.width *= scale;
    viewBox.height *= scale;
  });
}
