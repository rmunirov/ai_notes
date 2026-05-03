import { useEffect, useLayoutEffect, useRef } from "react";
import { useEditor, EditorContent } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";
import { useNotesStore } from "../../store/notesStore";
import { tokens } from "../../theme/tokens";

function syncTextareaHeight(el: HTMLTextAreaElement | null) {
  if (!el) return;
  el.style.height = "0px";
  el.style.height = `${Math.max(el.scrollHeight, 44)}px`;
}

export function NoteEditor() {
  const s = useNotesStore();
  const t = useRef<ReturnType<typeof setTimeout> | null>(null);
  const titleRef = useRef<HTMLTextAreaElement | null>(null);
  const editor = useEditor({
    extensions: [StarterKit],
    content: s.bodyHtml || "<p></p>",
    onUpdate: ({ editor }) => {
      const h = editor.getHTML();
      s.updateBody(s.bodyTitle, h);
      if (t.current) clearTimeout(t.current);
      t.current = setTimeout(() => void s.save(), 1000);
    },
  });
  useEffect(() => {
    if (editor && s.bodyHtml !== editor.getHTML()) {
      editor.commands.setContent(s.bodyHtml || "<p></p>", false);
    }
  }, [s.selected, s.bodyHtml, editor]);

  useLayoutEffect(() => {
    syncTextareaHeight(titleRef.current);
  }, [s.selected, s.bodyTitle]);

  if (!s.selected) {
    return (
      <div
        style={{
          flex: 1,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          padding: tokens.space.lg,
          color: tokens.colors.onSurfaceVariant,
          background: tokens.colors.surface,
          minWidth: 0,
        }}
      >
        Выберите заметку
      </div>
    );
  }
  return (
    <div
      style={{
        flex: 1,
        display: "flex",
        flexDirection: "column",
        minWidth: 0,
        minHeight: 0,
        background: tokens.colors.surface,
        padding: tokens.space.md,
        gap: 12,
        boxSizing: "border-box",
      }}
    >
      <div
        style={{
          background: tokens.colors.surfaceContainerHigh,
          borderRadius: tokens.radius.md,
          padding: "20px 20px 12px",
          flexShrink: 0,
          minWidth: 0,
        }}
      >
        <textarea
          ref={titleRef}
          className="note-editor-title"
          aria-label="Заголовок"
          rows={1}
          value={s.bodyTitle}
          onChange={(e) => {
            s.updateBody(e.target.value, s.bodyHtml);
            requestAnimationFrame(() => syncTextareaHeight(titleRef.current));
          }}
          onBlur={() => void s.save()}
          placeholder="Заголовок заметки"
          style={{
            display: "block",
            width: "100%",
            minWidth: 0,
            margin: 0,
            padding: 0,
            background: "transparent",
            color: tokens.colors.onSurfaceBright,
            border: "none",
            fontFamily: "inherit",
            fontSize: 28,
            fontWeight: 500,
            lineHeight: 1.25,
            outline: "none",
            resize: "none",
            overflow: "hidden",
          }}
        />
      </div>
      <div
        style={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          minHeight: 0,
          minWidth: 0,
          background: tokens.colors.surfaceContainerHigh,
          borderRadius: tokens.radius.md,
          padding: 20,
          boxSizing: "border-box",
        }}
      >
        <div className="note-editor-prose" style={{ flex: 1, overflow: "auto", minHeight: 0, minWidth: 0 }}>
          <EditorContent editor={editor} />
        </div>
        <div
          style={{
            flexShrink: 0,
            fontSize: 12,
            color: tokens.colors.onSurfaceVariant,
            paddingTop: 12,
            textAlign: "left",
          }}
        >
          Автосохранение с debounce 1s.
        </div>
      </div>
    </div>
  );
}
