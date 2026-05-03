await figma.loadFontAsync({ family: "Inter", style: "Regular" });
await figma.loadFontAsync({ family: "Inter", style: "Semi Bold" });
const D={bg:{r:.086,g:.09,b:.098},sf:{r:.14,g:.145,b:.16},hi:{r:.22,g:.225,b:.25},t:{r:.96,g:.97,b:1},m:{r:.55,g:.58,b:.62},a:{r:.545,g:.365,b:.965},b:{r:.26,g:.28,b:.32},w:{r:1,g:1,b:1},x:{r:.22,g:.2,b:.32}};
function V(n){const f=figma.createFrame();f.layoutMode="VERTICAL";f.primaryAxisSizingMode="AUTO";f.counterAxisSizingMode="AUTO";if(n)f.name=n;return f;}
function H(n){const f=figma.createFrame();f.layoutMode="HORIZONTAL";f.primaryAxisSizingMode="AUTO";f.counterAxisSizingMode="AUTO";if(n)f.name=n;return f;}
const T=(s,z,c,B)=>{const t=figma.createText();t.characters=s;t.fontSize=z;t.fontName=B?{family:"Inter",style:"Semi Bold"}:{family:"Inter",style:"Regular"};t.lineHeight={unit:"AUTO"};t.fills=[{type:"SOLID",color:c||D.t}];return t};
const P=(f,l,t,r,b)=>{f.paddingLeft=l;f.paddingTop=t;f.paddingRight=r;f.paddingBottom=b};
const rid="__RID__";
const root=await figma.getNodeByIdAsync(rid);
const main=root.children.find(n=>n.name==="Main")||root.children[0];
const ed=V("Editor");ed.fills=[{type:"SOLID",color:D.bg}];ed.resizeWithoutConstraints(636,800);ed.itemSpacing=0;P(ed,20,0,20,0);
const eh=H("title bar");eh.itemSpacing=0;eh.primaryAxisAlignItems="CENTER";eh.layoutSizingHorizontal="FILL";const lt=H();lt.itemSpacing=8;lt.appendChild(T("📌",14,D.m,0));lt.appendChild(T("Заголовок заметки",22,D.t,1));eh.appendChild(lt);const sph=V();sph.layoutGrow=1;sph.layoutSizingHorizontal="FILL";eh.appendChild(sph);const rt=H();rt.itemSpacing=10;rt.primaryAxisAlignItems="CENTER";rt.appendChild(T("Сохранено • 10:30",13,D.m,0));rt.appendChild(T("⋯",20,D.m,0));eh.appendChild(rt);P(eh,0,16,0,12);
const tb=H("Toolbar");tb.fills=[{type:"SOLID",color:D.sf}];tb.cornerRadius=8;tb.strokeWeight=1;tb.strokes=[{type:"SOLID",color:D.b}];tb.itemSpacing=12;tb.primaryAxisAlignItems="CENTER";P(tb,12,8,12,8);["H1","H2","H3"].forEach(x=>tb.appendChild(T(x,13,D.m,0)));tb.appendChild(T("B",13,D.t,1));tb.appendChild(T("I",13,D.t,0));["•","1.","☑","❝","🔗","🖼"].forEach(x=>tb.appendChild(T(x,13,D.m,0)));const txs=V();txs.layoutGrow=1;txs.layoutSizingHorizontal="FILL";tb.appendChild(txs);tb.appendChild(T("↶",16,D.m,0));tb.appendChild(T("↷",16,D.m,0));
const bd=V("Body");bd.itemSpacing=8;bd.layoutSizingVertical="FILL";bd.layoutSizingHorizontal="FILL";bd.layoutGrow=1;bd.appendChild(T("Текст заметки (rich text, StarterKit). Автосохранение с debounce 1s.",15,D.m,0));
const ef=H("footer");ef.primaryAxisAlignItems="CENTER";const eL=H();eL.appendChild(T("232 слова • 1 234 символа",12,D.m,0));ef.appendChild(eL);const eS=V();eS.layoutGrow=1;eS.layoutSizingHorizontal="FILL";ef.appendChild(eS);ef.appendChild(T("?",14,D.m,0));P(ef,0,12,0,16);
ed.appendChild(eh);ed.appendChild(tb);ed.appendChild(bd);ed.appendChild(ef);main.appendChild(ed);
const ag=V("AI агент");ag.fills=[{type:"SOLID",color:D.sf}];ag.strokes=[{type:"SOLID",color:D.b}];ag.strokeWeight=1;ag.resize(360,800);ag.itemSpacing=16;P(ag,16,16,16,12);
const at=H("header");at.itemSpacing=8;at.primaryAxisAlignItems="CENTER";at.appendChild(T("✦",16,D.a,0));at.appendChild(T("AI агент",16,D.t,1));const as=V();as.layoutGrow=1;as.layoutSizingHorizontal="FILL";at.appendChild(as);at.appendChild(T("Скрыть",13,D.a,0));ag.appendChild(at);ag.appendChild(T("Я отвечу на вопросы по вашим заметкам и помогу найти нужную информацию.",13,D.m,0));ag.appendChild(T("Примеры вопросов",12,D.m,1));
const ex=q=>{const bx=V();bx.fills=[{type:"SOLID",color:D.hi}];bx.cornerRadius=8;bx.strokes=[{type:"SOLID",color:D.b}];bx.strokeWeight=1;P(bx,12,10,12,10);bx.appendChild(T(q,13,D.t,0));return bx;};
ag.appendChild(ex("Какие темы чаще всего встречаются в моих заметках?"));ag.appendChild(ex("Найди упоминания про искусственный интеллект"));ag.appendChild(ex("Что было в заметках на прошлой неделе?"));
const agG=figma.createFrame();agG.name="sp";agG.layoutMode="VERTICAL";agG.layoutGrow=1;agG.resize(12,28);agG.fills=[];
const ir=H("input");ir.fills=[{type:"SOLID",color:D.hi}];ir.cornerRadius=12;ir.strokes=[{type:"SOLID",color:D.b}];ir.itemSpacing=8;ir.primaryAxisAlignItems="CENTER";P(ir,12,10,12,10);ir.layoutSizingHorizontal="FILL";const it=V();it.layoutGrow=1;it.layoutSizingHorizontal="FILL";it.appendChild(T("Спросите что угодно о ваших заметках…",14,D.m,0));ir.appendChild(it);const sd=V();sd.resize(40,40);sd.cornerRadius=20;sd.primaryAxisAlignItems="CENTER";sd.counterAxisAlignItems="CENTER";sd.fills=[{type:"SOLID",color:D.a}];sd.appendChild(T("➤",16,D.w,0));ir.appendChild(sd);
const ad=H();ad.itemSpacing=6;ad.primaryAxisAlignItems="CENTER";ad.appendChild(T("ⓘ",12,D.m,0));ad.appendChild(T("Ответы основаны только на ваших заметках",11,D.m,0));ag.appendChild(agG);ag.appendChild(ir);ag.appendChild(ad);main.appendChild(ag);
const section=await figma.getNodeByIdAsync("17:2");
section.appendChild(root);
return { ok: true, theme: "dark", rootId: root.id };
