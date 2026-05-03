await figma.loadFontAsync({ family: "Inter", style: "Regular" });
await figma.loadFontAsync({ family: "Inter", style: "Semi Bold" });
const D={bg:{r:.086,g:.09,b:.098},sf:{r:.14,g:.145,b:.16},hi:{r:.22,g:.225,b:.25},t:{r:.96,g:.97,b:1},m:{r:.55,g:.58,b:.62},a:{r:.545,g:.365,b:.965},b:{r:.26,g:.28,b:.32},w:{r:1,g:1,b:1},x:{r:.22,g:.2,b:.32}};
function V(n){const f=figma.createFrame();f.layoutMode="VERTICAL";f.primaryAxisSizingMode="AUTO";f.counterAxisSizingMode="AUTO";if(n)f.name=n;return f;}
function H(n){const f=figma.createFrame();f.layoutMode="HORIZONTAL";f.primaryAxisSizingMode="AUTO";f.counterAxisSizingMode="AUTO";if(n)f.name=n;return f;}
const T=(s,z,c,B)=>{const t=figma.createText();t.characters=s;t.fontSize=z;t.fontName=B?{family:"Inter",style:"Semi Bold"}:{family:"Inter",style:"Regular"};t.lineHeight={unit:"AUTO"};t.fills=[{type:"SOLID",color:c||D.t}];return t};
const P=(f,l,t,r,b)=>{f.paddingLeft=l;f.paddingTop=t;f.paddingRight=r;f.paddingBottom=b};
const root=V("Тёмная тема");root.fills=[{type:"SOLID",color:D.bg}];root.resize(1280,800);root.counterAxisSizingMode="FIXED";
const main=H("Main");main.resize(1280,800);main.itemSpacing=0;main.counterAxisSizingMode="FIXED";
const sb=V("Sidebar");sb.fills=[{type:"SOLID",color:D.sf}];sb.strokes=[{type:"SOLID",color:D.b}];sb.strokeWeight=1;sb.resize(284,800);sb.itemSpacing=14;P(sb,14,16,14,12);
const top=H("top");top.itemSpacing=8;top.fills=[];
const b1=H();b1.fills=[{type:"SOLID",color:D.a}];b1.cornerRadius=10;P(b1,16,10,16,10);b1.appendChild(T("Новая заметка",14,D.w,0));const b2=H();b2.fills=[{type:"SOLID",color:D.hi}];b2.cornerRadius=10;P(b2,14,10,14,10);b2.appendChild(T("Удалить",14,D.t,0));const b3=H();b3.fills=[{type:"SOLID",color:D.hi}];b3.cornerRadius=8;P(b3,10,8,10,8);b3.appendChild(T("▦",14,D.m,0));top.appendChild(b1);top.appendChild(b2);top.appendChild(b3);
const sr=H("Поиск");sr.fills=[{type:"SOLID",color:D.hi}];sr.strokes=[{type:"SOLID",color:D.b}];sr.strokeWeight=1;sr.cornerRadius=10;sr.itemSpacing=8;sr.primaryAxisAlignItems="CENTER";P(sr,12,10,12,10);
const sm=V();const st=H();st.appendChild(T("Поиск заметок…",14,D.m,0));sm.appendChild(st);
sr.appendChild(T("⌕",16,D.m,0));sr.appendChild(sm);sr.appendChild(T("⌘K",12,D.m,0));

const nr=(ti,pr,tm,ac)=>{const r=H();r.cornerRadius=8;r.itemSpacing=8;r.primaryAxisAlignItems="CENTER";r.fills=[{type:"SOLID",color:ac?D.x:D.hi}];if(ac){r.strokes=[{type:"SOLID",color:D.a}];r.strokeWeight=1}P(r,10,8,10,8);if(ac){const s=figma.createRectangle();s.resize(3,36);s.cornerRadius=1.5;s.fills=[{type:"SOLID",color:D.a}];r.appendChild(s)}const c=V();c.itemSpacing=4;c.appendChild(T(ti,14,D.t,1));c.appendChild(T(pr,12,D.m,0));r.appendChild(c);c.layoutSizingHorizontal="FILL";r.appendChild(T(tm,12,D.m,0));return r;};
const li=V();li.itemSpacing=8;li.appendChild(nr("Заметка 1","Превью…","10:30",1));li.appendChild(nr("Заметка 2","Превью…","Вчера",0));li.appendChild(nr("Заметка 3","Превью…","12 мая",0));

const g=figma.createFrame();g.name="s";g.layoutMode="VERTICAL";g.resize(24,36);g.fills=[];
const ft=H();ft.itemSpacing=10;ft.primaryAxisAlignItems="CENTER";const gr=H();gr.appendChild(T("⚙",18,D.m,0));ft.appendChild(gr);const av=V();av.cornerRadius=16;av.resize(32,32);av.primaryAxisAlignItems="CENTER";av.counterAxisAlignItems="CENTER";av.fills=[{type:"SOLID",color:D.a}];av.appendChild(T("A",13,D.w,1));ft.appendChild(av);const nc=V();nc.appendChild(T("Алексей",14,D.t,0));ft.appendChild(nc);
sb.appendChild(top);sb.appendChild(sr);sb.appendChild(li);sb.appendChild(g);sb.appendChild(ft);
sr.layoutSizingHorizontal="FILL";sm.layoutGrow=1;sm.layoutSizingHorizontal="FILL";li.layoutSizingVertical="FILL";li.layoutSizingHorizontal="FILL";g.layoutGrow=1;
main.appendChild(sb);
root.appendChild(main);
return {rootId:root.id,mainId:main.id};
