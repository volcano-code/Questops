import { describe, expect, it } from "vitest";
import { buildRunBody } from "./api";

describe("run request policy", () => {
  it("never marks fixture as a model call", () => {
    expect(buildRunBody(" canonical ", "fixture", true)).toEqual({
      intent: "canonical", mode: "fixture", allow_model_call: false,
    });
  });

  it("requires explicit live consent", () => {
    expect(buildRunBody("canonical", "live", false).allow_model_call).toBe(false);
    expect(buildRunBody("canonical", "live", true).allow_model_call).toBe(true);
  });
});
