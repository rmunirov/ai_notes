await figma.loadFontAsync({ family: "Inter", style: "Regular" });
await figma.loadFontAsync({ family: "Inter", style: "Semi Bold" });
const D = {
  bg: { r: 0.086, g: 0.09, b: 0.098 },
  surface: { r: 0.14, g: 0.145, b: 0.16 },
  hi: { r: 0.22, g: 0.225, b: 0.25 },
  t: { r: 0.96, g: 0.97, b: 1 },
  m: { r: 0.55, g: 0.58, b: 0.62 },
  a: { r: 0.545, g: 0.365, b: 0.965 },
  b: { r: 0.26, g: 0.28, b: 0.32 },
  w: { r: 1, g: 1, b: 1 },
  x: { r: 0.22, g: 0.2, b: 0.32 },
};
function T(s, z, c, B) {
  const t = figma.createText();
  t.characters = s;
  t.fontSize = z;
  t.fontName = B ? { family: "Inter", style: "Semi Bold" } : { family: "Inter", style: "Regular" };
  t.lineHeight = { unit: "AUTO" };
  t.fills = [{ type: "SOLID", color: c || D.t }];
  return t;
}
function V(n) {
  const f = figma.createAutoLayout("VERTICAL");
  if (n) f.name = n;
  return f;
}
function H(n) {
  const f = figma.createAutoLayout("HORIZONTAL");
  if (n) f.name = n;
  return f;
}
function P(f, l, t, r, b) {
  f.paddingLeft = l;
  f.paddingTop = t;
  f.paddingRight = r;
  f.paddingBottom = b;
}

const root = V("Тёмная тема");
root.fills = [{ type: "SOLID", color: D.bg }];
root.resize(1280, 800);
const main = H("Main");
main.itemSpacing = 0;
main.resize(1280, 800);
const sb = V("Sidebar");
sb.fills = [{ type: "SOLID", color: D.surface }];
sb.strokes = [{ type: "SOLID", color: D.b }];
sb.strokeWeight = 1;
sb.resize(284, 800);
sb.itemSpacing = 14;
P(sb, 14, 16, 14, 12);
const top = H("top");
top.itemSpacing = 8;
top.fills = [];
const b1 = H("Новая заметка");
b1.fills = [{ type: "SOLID", color: D.a }];
b1.cornerRadius = 10;
P(b1, 16, 10, 16, 10);
b1.appendChild(T("Новая заметка", 14, D.w, 0));
const b2 = H("Удалить");
b2.fills = [{ type: "SOLID", color: D.hi }];
b2.cornerRadius = 10;
P(b2, 14, 10, 14, 10);
b2.appendChild(T("Удалить", 14, D.t, 0));
const b3 = H("Сетка");
b3.fills = [{ type: "SOLID", color: D.hi }];
b3.cornerRadius = 8;
P(b3, 10, 8, 10, 8);
b3.appendChild(T("▦", 14, D.m, 0));
top.appendChild(b1);
top.appendChild(b2);
top.appendChild(b3);
const sr = H("Поиск");
sr.fills = [{ type: "SOLID", color: D.hi }];
sr.strokes = [{ type: "SOLID", color: D.b }];
sr.strokeWeight = 1;
sr.cornerRadius = 10;
sr.itemSpacing = 8;
sr.primaryAxisAlignItems = "CENTER";
P(sr, 12, 10, 12, 10);
sr.layoutSizingHorizontal = "FILL";
sr.appendChild(T("⌕", 16, D.m, 0));
const sm = V();
sm.fills = [];
sm.layoutGrow = 1;
sm.layoutSizingHorizontal = "FILL";
const st = H();
st.fills = [];
st.appendChild(T("Поиск заметок…", 14, D.m, 0));
sm.appendChild(st);
sr.appendChild(sm);
sr.appendChild(T("⌘K", 12, D.m, 0));
function nr(ti, pr, tm, ac) {
  const r = H("Note");
  r.cornerRadius = 8;
  r.itemSpacing = 8;
  r.primaryAxisAlignItems = "CENTER";
  r.fills = [{ type: "SOLID", color: ac ? D.x : D.hi }];
  if (ac) {
    r.strokes = [{ type: "SOLID", color: D.a }];
    r.strokeWeight = 1;
  }
  P(r, 10, 8, 10, 8);
  if (ac) {
    const s = figma.createRectangle();
    s.resize(3, 36);
    s.cornerRadius = 1.5;
    s.fills = [{ type: "SOLID", color: D.a }];
    r.appendChild(s);
  }
  const c = V();
  c.fills = [];
  c.itemSpacing = 4;
  c.layoutSizingHorizontal = "FILL";
  c.appendChild(T(ti, 14, D.t, 1));
  c.appendChild(T(pr, 12, D.m, 0));
  r.appendChild(c);
  r.appendChild(T(tm, 12, D.m, 0));
  return r;
}
const li = V("Список");
li.fills = [];
li.itemSpacing = 8;
li.layoutSizingVertical = "FILL";
li.layoutSizingHorizontal = "FILL";
li.appendChild(nr("Заметка 1", "Превью заметки…", "10:30", 1));
li.appendChild(nr("Заметка 2", "Превью заметки…", "Вчера", 0));
li.appendChild(nr("Заметка 3", "Превью заметки…", "12 мая", 0));
const g = figma.createFrame();
g.name = "spacer";
g.fills = [];
g.layoutGrow = 1;
g.layoutMode = "VERTICAL";
g.resize(10, 20);
const ft = H("Профиль");
ft.itemSpacing = 10;
ft.primaryAxisAlignItems = "CENTER";
ft.fills = [];
const gr = H();
gr.appendChild(T("⚙", 18, D.m, 0));
gr.fills = [];
ft.appendChild(gr);
const av = figma.createAutoLayout("VERTICAL");
av.cornerRadius = 16;
av.resize(32, 32);
av.primaryAxisAlignItems = "CENTER";
av.counterAxisAlignItems = "CENTER";
av.fills = [{ type: "SOLID", color: D.a }];
av.appendChild(T("A", 13, D.w, 1));
ft.appendChild(av);
const nc = V();
nc.fills = [];
nc.appendChild(T("Алексей", 14, D.t, 0));
ft.appendChild(nc);
sb.appendChild(top);
sb.appendChild(sr);
sb.appendChild(li);
sb.appendChild(g);
sb.appendChild(ft);
main.appendChild(sb);
root.appendChild(main);
return { ok: true, phase: "dark_sidebar", rootId: root.id, mainId: main.id };
