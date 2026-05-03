await figma.loadFontAsync({ family: "Inter", style: "Regular" });
await figma.loadFontAsync({ family: "Inter", style: "Semi Bold" });

const D = {
  bg: { r: 0.086, g: 0.09, b: 0.098 },
  surface: { r: 0.14, g: 0.145, b: 0.16 },
  surfaceHi: { r: 0.22, g: 0.225, b: 0.25 },
  text: { r: 0.96, g: 0.97, b: 1 },
  muted: { r: 0.55, g: 0.58, b: 0.62 },
  accent: { r: 0.545, g: 0.365, b: 0.965 },
  border: { r: 0.26, g: 0.28, b: 0.32 },
  onAccent: { r: 1, g: 1, b: 1 },
  activeBg: { r: 0.22, g: 0.2, b: 0.32 },
};

function T(text, size, color, semi) {
  const t = figma.createText();
  t.characters = text;
  t.fontSize = size;
  t.fontName = semi
    ? { family: "Inter", style: "Semi Bold" }
    : { family: "Inter", style: "Regular" };
  t.lineHeight = { unit: "AUTO" };
  t.fills = [{ type: "SOLID", color: color || D.text }];
  return t;
}

function alv(name) {
  const f = figma.createAutoLayout("VERTICAL");
  if (name) f.name = name;
  return f;
}

function alh(name) {
  const f = figma.createAutoLayout("HORIZONTAL");
  if (name) f.name = name;
  return f;
}

function pad(f, l, t, r, b) {
  f.paddingLeft = l;
  f.paddingTop = t;
  f.paddingRight = r;
  f.paddingBottom = b;
}

const section = await figma.getNodeByIdAsync("17:2");
const createdNodeIds = [];

const root = alv("Тёмная тема");
root.fills = [{ type: "SOLID", color: D.bg }];
root.resize(1280, 800);
root.itemSpacing = 0;
root.cornerRadius = 0;

const main = alh("Main");
main.fills = [];
main.itemSpacing = 0;
main.resize(1280, 800);

const sidebar = alv("Sidebar");
sidebar.fills = [{ type: "SOLID", color: D.surface }];
sidebar.strokes = [{ type: "SOLID", color: D.border }];
sidebar.strokeWeight = 1;
sidebar.resize(284, 800);
sidebar.itemSpacing = 14;
pad(sidebar, 14, 16, 14, 12);

const top = alh("top");
top.itemSpacing = 8;
top.fills = [];

const b1 = alh("Новая заметка");
b1.fills = [{ type: "SOLID", color: D.accent }];
b1.cornerRadius = 10;
pad(b1, 16, 10, 16, 10);
b1.appendChild(T("Новая заметка", 14, D.onAccent, false));

const b2 = alh("Удалить");
b2.fills = [{ type: "SOLID", color: D.surfaceHi }];
b2.cornerRadius = 10;
pad(b2, 14, 10, 14, 10);
b2.appendChild(T("Удалить", 14, D.text, false));

const b3 = alh("Сетка");
b3.fills = [{ type: "SOLID", color: D.surfaceHi }];
b3.cornerRadius = 8;
pad(b3, 10, 8, 10, 8);
b3.appendChild(T("▦", 14, D.muted, false));

top.appendChild(b1);
top.appendChild(b2);
top.appendChild(b3);

const search = alh("Поиск");
search.fills = [{ type: "SOLID", color: D.surfaceHi }];
search.strokes = [{ type: "SOLID", color: D.border }];
search.strokeWeight = 1;
search.cornerRadius = 10;
search.itemSpacing = 8;
search.primaryAxisAlignItems = "CENTER";
pad(search, 12, 10, 12, 10);
search.layoutSizingHorizontal = "FILL";
search.appendChild(T("⌕", 16, D.muted, false));
const spMid = alv();
spMid.fills = [];
spMid.layoutGrow = 1;
spMid.layoutSizingHorizontal = "FILL";
const spText = alh();
spText.fills = [];
spText.appendChild(T("Поиск заметок…", 14, D.muted, false));
spMid.appendChild(spText);
search.appendChild(spMid);
search.appendChild(T("⌘K", 12, D.muted, false));

function noteRow(title, preview, time, active) {
  const row = alh("Note");
  row.cornerRadius = 8;
  row.itemSpacing = 8;
  row.primaryAxisAlignItems = "CENTER";
  row.fills = [{ type: "SOLID", color: active ? D.activeBg : D.surfaceHi }];
  if (active) {
    row.strokes = [{ type: "SOLID", color: D.accent }];
    row.strokeWeight = 1;
  }
  pad(row, 10, 8, 10, 8);
  if (active) {
    const stripe = figma.createRectangle();
    stripe.resize(3, 36);
    stripe.cornerRadius = 1.5;
    stripe.fills = [{ type: "SOLID", color: D.accent }];
    row.appendChild(stripe);
  }
  const col = alv();
  col.fills = [];
  col.itemSpacing = 4;
  col.layoutSizingHorizontal = "FILL";
  col.appendChild(T(title, 14, D.text, true));
  col.appendChild(T(preview, 12, D.muted, false));
  row.appendChild(col);
  row.appendChild(T(time, 12, D.muted, false));
  return row;
}

const list = alv("Список");
list.fills = [];
list.itemSpacing = 8;
list.layoutSizingVertical = "FILL";
list.layoutSizingHorizontal = "FILL";
list.appendChild(noteRow("Заметка 1", "Превью заметки…", "10:30", true));
list.appendChild(noteRow("Заметка 2", "Превью заметки…", "Вчера", false));
list.appendChild(noteRow("Заметка 3", "Превью заметки…", "12 мая", false));

const grow = figma.createFrame();
grow.name = "spacer";
grow.fills = [];
grow.layoutGrow = 1;
grow.layoutMode = "VERTICAL";
grow.resize(10, 20);

const foot = alh("Профиль");
foot.itemSpacing = 10;
foot.primaryAxisAlignItems = "CENTER";
foot.fills = [];
const gear = alh();
gear.appendChild(T("⚙", 18, D.muted, false));
gear.fills = [];
foot.appendChild(gear);
const avatar = figma.createAutoLayout("VERTICAL");
avatar.cornerRadius = 16;
avatar.resize(32, 32);
avatar.primaryAxisAlignItems = "CENTER";
avatar.counterAxisAlignItems = "CENTER";
avatar.fills = [{ type: "SOLID", color: D.accent }];
avatar.appendChild(T("A", 13, D.onAccent, true));
foot.appendChild(avatar);
const nameCol = alv();
nameCol.fills = [];
nameCol.appendChild(T("Алексей", 14, D.text, false));
foot.appendChild(nameCol);

sidebar.appendChild(top);
sidebar.appendChild(search);
sidebar.appendChild(list);
sidebar.appendChild(grow);
sidebar.appendChild(foot);

main.appendChild(sidebar);

const editor = alv("Editor");
editor.fills = [{ type: "SOLID", color: D.bg }];
editor.resizeWithoutConstraints(636, 800);
editor.itemSpacing = 0;
pad(editor, 20, 0, 20, 0);

const edHead = alh("title bar");
edHead.itemSpacing = 0;
edHead.primaryAxisAlignItems = "CENTER";
edHead.layoutSizingHorizontal = "FILL";
const leftT = alh();
leftT.itemSpacing = 8;
leftT.fills = [];
leftT.appendChild(T("📌", 14, D.muted, false));
leftT.appendChild(T("Заголовок заметки", 22, D.text, true));
edHead.appendChild(leftT);
const sph = alv();
sph.fills = [];
sph.layoutGrow = 1;
sph.layoutSizingHorizontal = "FILL";
edHead.appendChild(sph);
const rightT = alh();
rightT.itemSpacing = 10;
rightT.fills = [];
rightT.primaryAxisAlignItems = "CENTER";
rightT.appendChild(T("Сохранено • 10:30", 13, D.muted, false));
rightT.appendChild(T("⋯", 20, D.muted, false));
edHead.appendChild(rightT);

pad(edHead, 0, 16, 0, 12);

const toolbar = alh("Toolbar");
toolbar.fills = [{ type: "SOLID", color: D.surface }];
toolbar.cornerRadius = 8;
toolbar.strokeWeight = 1;
toolbar.strokes = [{ type: "SOLID", color: D.border }];
toolbar.itemSpacing = 12;
toolbar.primaryAxisAlignItems = "CENTER";
pad(toolbar, 12, 8, 12, 8);
toolbar.appendChild(T("H1", 13, D.muted, false));
toolbar.appendChild(T("H2", 13, D.muted, false));
toolbar.appendChild(T("H3", 13, D.muted, false));
toolbar.appendChild(T("B", 13, D.text, true));
toolbar.appendChild(T("I", 13, D.text, false));
toolbar.appendChild(T("•", 13, D.muted, false));
toolbar.appendChild(T("1.", 13, D.muted, false));
toolbar.appendChild(T("☑", 13, D.muted, false));
toolbar.appendChild(T("❝", 13, D.muted, false));
toolbar.appendChild(T("🔗", 13, D.muted, false));
toolbar.appendChild(T("🖼", 13, D.muted, false));
const tbSp = alv();
tbSp.fills = [];
tbSp.layoutGrow = 1;
tbSp.layoutSizingHorizontal = "FILL";
toolbar.appendChild(tbSp);
toolbar.appendChild(T("↶", 16, D.muted, false));
toolbar.appendChild(T("↷", 16, D.muted, false));

const body = alv("Body");
body.fills = [];
body.itemSpacing = 8;
body.layoutSizingVertical = "FILL";
body.layoutSizingHorizontal = "FILL";
body.layoutGrow = 1;
body.appendChild(
  T(
    "Текст заметки (rich text, StarterKit). Автосохранение с debounce 1s.",
    15,
    D.muted,
    false
  )
);

const edFoot = alh("footer");
edFoot.fills = [];
edFoot.itemSpacing = 0;
edFoot.primaryAxisAlignItems = "CENTER";
const efL = alh();
efL.appendChild(T("232 слова • 1 234 символа", 12, D.muted, false));
edFoot.appendChild(efL);
const efSp = alv();
efSp.fills = [];
efSp.layoutGrow = 1;
efSp.layoutSizingHorizontal = "FILL";
edFoot.appendChild(efSp);
edFoot.appendChild(T("?", 14, D.muted, false));
pad(edFoot, 0, 12, 0, 16);

editor.appendChild(edHead);
editor.appendChild(toolbar);
editor.appendChild(body);
editor.appendChild(edFoot);

main.appendChild(editor);

const agent = alv("AI агент");
agent.fills = [{ type: "SOLID", color: D.surface }];
agent.strokes = [{ type: "SOLID", color: D.border }];
agent.strokeWeight = 1;
agent.resize(360, 800);
agent.itemSpacing = 16;
pad(agent, 16, 16, 16, 12);

const agTop = alh("header");
agTop.fills = [];
agTop.itemSpacing = 8;
agTop.primaryAxisAlignItems = "CENTER";
agTop.appendChild(T("✦", 16, D.accent, false));
agTop.appendChild(T("AI агент", 16, D.text, true));
const agSp = alv();
agSp.fills = [];
agSp.layoutGrow = 1;
agSp.layoutSizingHorizontal = "FILL";
agTop.appendChild(agSp);
agTop.appendChild(T("Скрыть", 13, D.accent, false));

agent.appendChild(agTop);
agent.appendChild(
  T(
    "Я отвечу на вопросы по вашим заметкам и помогу найти нужную информацию.",
    13,
    D.muted,
    false
  )
);

const exTitle = T("Примеры вопросов", 12, D.muted, true);
agent.appendChild(exTitle);

function exBox(q) {
  const bx = alv();
  bx.fills = [{ type: "SOLID", color: D.surfaceHi }];
  bx.cornerRadius = 8;
  bx.strokes = [{ type: "SOLID", color: D.border }];
  bx.strokeWeight = 1;
  pad(bx, 12, 10, 12, 10);
  bx.appendChild(T(q, 13, D.text, false));
  return bx;
}

agent.appendChild(
  exBox("Какие темы чаще всего встречаются в моих заметках?")
);
agent.appendChild(exBox("Найди упоминания про искусственный интеллект"));
agent.appendChild(exBox("Что было в заметках на прошлой неделе?"));

const agGrow = figma.createFrame();
agGrow.name = "sp";
agGrow.fills = [];
agGrow.layoutGrow = 1;
agGrow.layoutMode = "VERTICAL";
agGrow.resize(10, 20);

const inputRow = alh("input");
inputRow.fills = [{ type: "SOLID", color: D.surfaceHi }];
inputRow.cornerRadius = 12;
inputRow.strokes = [{ type: "SOLID", color: D.border }];
inputRow.itemSpacing = 8;
inputRow.primaryAxisAlignItems = "CENTER";
pad(inputRow, 12, 10, 12, 10);
inputRow.layoutSizingHorizontal = "FILL";
const inpText = alv();
inpText.fills = [];
inpText.layoutGrow = 1;
inpText.layoutSizingHorizontal = "FILL";
inpText.appendChild(T("Спросите что угодно о ваших заметках…", 14, D.muted, false));
inputRow.appendChild(inpText);
const send = figma.createAutoLayout("VERTICAL");
send.resize(40, 40);
send.cornerRadius = 20;
send.primaryAxisAlignItems = "CENTER";
send.counterAxisAlignItems = "CENTER";
send.fills = [{ type: "SOLID", color: D.accent }];
send.appendChild(T("➤", 16, D.onAccent, false));
inputRow.appendChild(send);

const agDisclaimer = alh("disc");
agDisclaimer.fills = [];
agDisclaimer.itemSpacing = 6;
agDisclaimer.primaryAxisAlignItems = "CENTER";
agDisclaimer.appendChild(T("ⓘ", 12, D.muted, false));
agDisclaimer.appendChild(
  T("Ответы основаны только на ваших заметках", 11, D.muted, false)
);

agent.appendChild(agGrow);
agent.appendChild(inputRow);
agent.appendChild(agDisclaimer);

main.appendChild(agent);
root.appendChild(main);
section.appendChild(root);

createdNodeIds.push(root.id, main.id, sidebar.id, editor.id, agent.id);

return { ok: true, theme: "dark", createdNodeIds };
