/**
 * Jest test suite for viewer/overlays.js
 *
 * Uses JSDOM to simulate the browser environment.
 */

import fs from "fs";
import path from "path";
import { JSDOM } from "jsdom";

// Load overlays.js source
const overlaysJs = fs.readFileSync(
  path.join(__dirname, "../overlays.js"),
  "utf8"
);

function setupDom(svgContent = "<svg></svg>") {
  const html = `
    <html>
      <body>
        <div id="svgContainer">${svgContent}</div>

        <input type="checkbox" id="show-bands">
        <input type="checkbox" id="show-order">
        <input type="checkbox" id="show-inout">
        <input type="checkbox" id="show-measure">
      </body>
    </html>
  `;

  const dom = new JSDOM(html, {
    runScripts: "dangerously",
    resources: "usable",
  });

  const { window } = dom;

  // Inject overlays.js
  const scriptEl = window.document.createElement("script");
  scriptEl.textContent = overlaysJs;
  window.document.body.appendChild(scriptEl);

  return window;
}

describe("Overlay system", () => {
  test("creates overlay layer when SVG is loaded", () => {
    const window = setupDom("<svg></svg>");
    const svg = window.document.querySelector("svg");

    const overlay = svg.querySelector("#overlay-layer");
    expect(overlay).not.toBeNull();
  });

  test("drawBands() creates 5 band rectangles", () => {
    const window = setupDom(`
      <svg>
        <rect x="0" y="-100" width="50" height="50" />
      </svg>
    `);

    const checkbox = window.document.getElementById("show-bands");
    checkbox.checked = true;
    checkbox.dispatchEvent(new window.Event("change"));

    const overlay = window.document.querySelector("#overlay-layer");
    const bands = overlay.querySelectorAll(".overlay-band");

    expect(bands.length).toBe(5);
  });

  test("drawOrder() labels rectangles in order", () => {
    const window = setupDom(`
      <svg>
        <rect x="10" y="-90" width="20" height="20" />
        <rect x="40" y="-80" width="20" height="20" />
      </svg>
    `);

    const checkbox = window.document.getElementById("show-order");
    checkbox.checked = true;
    checkbox.dispatchEvent(new window.Event("change"));

    const labels = window.document.querySelectorAll(".overlay-order");

    expect(labels.length).toBe(2);
    expect(labels[0].textContent).toBe("1");
    expect(labels[1].textContent).toBe("2");
  });

  test("drawInOut() detects only circle[data-type]", () => {
    const window = setupDom(`
      <svg>
        <circle cx="10" cy="-10" data-type="in" />
        <circle cx="20" cy="-20" data-type="out" />
        <circle cx="30" cy="-30" data-measure="1" />
      </svg>
    `);

    const checkbox = window.document.getElementById("show-inout");
    checkbox.checked = true;
    checkbox.dispatchEvent(new window.Event("change"));

    const overlay = window.document.querySelector("#overlay-layer");
    const dots = overlay.querySelectorAll(".overlay-point-in, .overlay-point-out");

    expect(dots.length).toBe(2);
  });

  test("drawMeasurement() detects measurement lines + points", () => {
    const window = setupDom(`
      <svg>
        <line x1="0" y1="0" x2="10" y2="10" data-measure="1" />
        <circle cx="5" cy="-5" data-measure="1" />
      </svg>
    `);

    const checkbox = window.document.getElementById("show-measure");
    checkbox.checked = true;
    checkbox.dispatchEvent(new window.Event("change"));

    const overlay = window.document.querySelector("#overlay-layer");

    const lines = overlay.querySelectorAll(".overlay-measure-line");
    const points = overlay.querySelectorAll(".overlay-measure-point");

    expect(lines.length).toBe(1);
    expect(points.length).toBe(1);
  });

  test("clearing overlay removes all overlay elements", () => {
    const window = setupDom(`
      <svg>
        <rect x="0" y="-10" width="10" height="10" />
      </svg>
    `);

    const checkbox = window.document.getElementById("show-order");
    checkbox.checked = true;
    checkbox.dispatchEvent(new window.Event("change"));

    const overlay = window.document.querySelector("#overlay-layer");
    expect(overlay.children.length).toBeGreaterThan(0);

    checkbox.checked = false;
    checkbox.dispatchEvent(new window.Event("change"));

    expect(overlay.children.length).toBe(0);
  });
});
