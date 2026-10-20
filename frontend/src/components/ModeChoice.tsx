// "Add" or "Replace" — how new data is combined with what the search index holds.
// A small switch: adding is the everyday choice, replacing the exception.

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
      <div className="mode-switch">
        {(["append", "replace"] as IngestMode[]).map((option) => (
          <label key={option} className={`mode-option ${mode === option ? "mode-active" : ""}`}>
            <input
              type="radio"
              name="mode"
              value={option}
              checked={mode === option}
              onChange={() => onChange(option)}
            />
            {option === "append" ? t.modeAppend : t.modeReplace}
          </label>
        ))}
      </div>
      <p className={`mode-hint ${mode === "replace" ? "mode-hint-warn" : ""}`}>
        {mode === "append" ? t.modeAppendHint : t.modeReplaceHint}
      </p>
    </fieldset>
  );
}
