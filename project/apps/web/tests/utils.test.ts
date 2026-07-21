import { cn } from "@/lib/utils";

describe("cn", () => {
  it("merges class names", () => {
    expect(cn("foo", "bar")).toBe("foo bar");
  });

  it("conditionally applies classes", () => {
    expect(cn("foo", false && "bar", "baz")).toBe("foo baz");
  });

  it("handles tailwind merge conflicts", () => {
    expect(cn("p-4", "p-6")).toBe("p-6");
  });
});
