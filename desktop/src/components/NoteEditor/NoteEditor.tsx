import { useEffect } from "react";
import { useEditor, EditorContent } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";
import { useNotesStore } from "../../store/notesStore";
import { tokens } from "../../theme/tokens";
import { useRef } from "react";

export function NoteEditor() {
  const s = useNotesStore();
  const t = useRef<ReturnType<typeof setTimeout> | null>(null);
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
  if (!s.selected) {
    return (
      <div style={{ padding: 24, color: tokens.colors.textMuted }}>Выберите заметку</div>
    );
  }
  return (
    <div style={{ flex: 1, display: "flex", flexDirection: "column" }}>
      <input
        aria-label="Заголовок"
        value={s.bodyTitle}
        onChange={(e) => s.updateBody(e.target.value, s.bodyHtml)}
        onBlur={() => void s.save()}
        style={{ fontSize: 20, margin: 16, background: tokens.colors.bg, color: tokens.colors.text, border: "none" }}
      />
      <div style={{ flex: 1, padding: 16, overflow: "auto" }}>
        <EditorContent editor={editor} />
      </div>
    </div>
  );
}
