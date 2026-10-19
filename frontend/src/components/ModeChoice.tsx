// "Add" or "Replace" — how new data is combined with what the search index holds.

import { useI18n } from "../i18n";
import type { IngestMode } from "../types";

export function ModeChoice({
  mode,
  onChange,
  disabled,
}: {
  mode: IngestMode;
  onChange: (mode: IngestMode) => void;
  disabled?: boolean;
}) {
  const { t } = useI18n();
  return (
    <fieldset className="mode" disabled={disabled}>
      <legend className="label">{t.modeTitle}</legend>
      {(["append", "replace"] as IngestMode[]).map((option) => (
        <label key={option} className={`mode-option ${mode === option ? "mode-active" : ""}`}>
          <input type="radio" name="mode" value={option} checked={mode === option} onChange={() => onChange(option)} />
          <span>
            <strong>{option === "append" ? t.modeAppend : t.modeReplace}</strong>
            <span className="muted">{option === "append" ? t.modeAppendHint : t.modeReplaceHint}</span>
          </span>
        </label>
      ))}
    </fieldset>
  );
}
