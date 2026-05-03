
await figma.loadFontAsync({ family: "Inter", style: "Regular" });
await figma.loadFontAsync({ family: "Inter", style: "Medium" });
await figma.loadFontAsync({ family: "Inter", style: "Semi Bold" });

const D = {
  bg: { r: 0.086, g: 0.09, b: 0.098 },
  surface: { r: 0.14, g: 0.145, b: 0.16 },
  surfaceHi: { r: 0.2, g: 0.205, b: 0.22 },
  text: { r: 0.96, g: 0.97, b: 1 },
  muted: { r: 0.55, g: 0.58, b: 0.62 },
  accent: { r: 0.545, g: 0.365, b: 0.965 },
  border: { r: 0.26, g: 0.28, b: 0.32 },
  onAccent: { r: 1, g: 1, b: 1 },
};

function T(txt, opts) {
  const t = figma.createText();
  t.characters = txt;
  t.fontSize = opts.size || 14;
  t.fontName = opts.semi ? { family: "Inter", style: "Semi Bold" } : { family: "Inter", style: "Regular" };
  t.lineHeight = { unit: "AUTO" };
  t.fills = [{ type: "SOLID", color: opts.color || D.text }];
  return t;
}

const section = await figma.getNodeByIdAsync("17:2");
const ids = [];

const wrapper = figma.createAutoLayout("VERTICAL");
wrapper.name = "Тёмная тема";
wrapper.itemSpacing = 0;
wrapper.fills = [];
wrapper.paddingLeft = 20;
wrapper.paddingTop = 20;
wrapper.paddingRight = 20;
wrapper.paddingBottom = 20);

function al(dir, opts) {
  const f = figma.createAutoLayout(dir);
  if (opts.name) f.name = opts.name;
  if (opts.fill !== undefined && opts.fill !== null) f.fills = [{ type: "SOLID", color: opts.fill }];
  if (opts.stroke) {
    f.strokes = [{ type: "SOLID", color: opts.stroke }];
    f.strokeWeight = 1;
  }
  if (opts.radius !== undefined) f.cornerRadius = opts.radius;
  if (opts.gap !== undefined) f.itemSpacing = opts.gap;
  if (opts.pad) {
    f.paddingLeft = f.paddingRight = opts.pad[1] || opts.pad[0];
    f.paddingTop = f.paddingBottom = opts.pad[0];
    if (opts.pad.length > 2) {
      f.paddingTop = opts.pad[0]; f.paddingRight = opts.pad[1]; f.paddingBottom = opts.pad[2]; f.paddingLeft = opts.pad[3] || opts.pad[1];
    }
  }
  return f;
}

const row = al("HORIZONTAL", { name: "Main" });
row.itemSpacing = 0;
row.resize(1280, 800);
row.counterAxisSizingMode = "AUTO";

const sidebar = al("VERTICAL", { name: "Sidebar", fill: D.surface, stroke: D.border });
sidebar.strokeWeight = 1;
sidebar.layoutSizingHorizontal = "FIXED";
sidebar.layoutSizingVertical = "FILL";
sidebar.resize(284, 800);
sidebar.itemSpacing = 14;
sidebar.paddingLeft = 14;
sidebar.paddingRight = 14;
sidebar.paddingTop = 16;
sidebar.paddingBottom = 14);
sidebar.cornerRadius = 0);

const acts = al("HORIZONTAL", { name: "Actions", gap: 8 });
acts.primaryAxisSizingMode = "AUTO";
acts.counterAxisSizingMode = "AUTO";

const bn = al("HORIZONTAL", { name: "Новая заметка", fill: D.accent, radius: 10 });
bn.paddingLeft = 16;
bn.paddingRight = 16;
bn.paddingTop = 10;
bn.paddingBottom = 10;
bn.primaryAxisSizingMode = "AUTO");
bn.counterAxisSizingMode = "AUTO");
bn.appendChild(T("Новая заметка", { color: D.onAccent, size: 14 }));

const bd = al("HORIZONTAL", { name: "Удалить", fill: D.btnGhost ?? D.surfaceHi, radius: 10 });