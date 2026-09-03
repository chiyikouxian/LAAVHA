#!/usr/bin/env python3
"""Prove the migration changed only markup, never prose/equations/data.

Normalises both files down to comparable plain text and diffs them.
"""
import re
import pathlib
import difflib

old = pathlib.Path("../manuscript_en.tex").read_text(encoding="utf-8")
new = pathlib.Path("main.tex").read_text(encoding="utf-8")


def body_of(text, start_marker, end_marker):
    return text[text.index(start_marker):text.index(end_marker)]


old_body = body_of(old, r"\section{Introduction}", r"\section*{References}")
new_body = body_of(new, r"\section{Introduction}", r"\vspace{6pt}")


def normalise(t):
    # Migration scaffolding comments are not manuscript content.
    t = re.sub(r"^%={5,}\s*$", "", t, flags=re.MULTILINE)
    # citation commands -> a single neutral token
    t = re.sub(r"\\upcite\{[0-9-]+\}", "@CITE@", t)
    t = re.sub(r"\\cite[pt]\{[^}]*\}", "@CITE@", t)
    # section cross-refs -> neutral token
    t = re.sub(r"Section~\\ref\{sec:[a-z]+\}", "@SEC@", t)
    t = re.sub(r"Section[~ ][0-9](\.[0-9])?", "@SEC@", t)
    # our added labels and heading de-decoration
    t = re.sub(r"\\label\{sec:[a-z]+\}", "", t)
    t = re.sub(r"\\textmd\{\\textit\{(.+?)\}\}", r"\1", t)
    # figure naming convention
    t = t.replace(r"Fig.~\ref", r"Figure~\ref")
    # the Figure 3 note moved from a standalone paragraph into \caption{};
    # reduce both forms to the same token so only the wording is compared
    t = re.sub(r"\{\\small \((For \(b\) and \(c\).+?delays\.)\)\\par\}",
               r"@NOTE@ \1", t)
    t = re.sub(r"enhancement parameters\. (For \(\\textbf\{b\}\) and .+?delays)\.\}",
               lambda m: "enhancement parameters.}\n@NOTE@ "
                         + m.group(1).replace(r"\textbf{b}", "b")
                                     .replace(r"\textbf{c}", "c")
                                     .replace("~", " ") + ".",
               t)
    # table environment swap
    t = t.replace("tabularx", "tabular")
    t = re.sub(r"\\begin\{tabular\}\{[^}]*(\}[^}]*)*?\}\n", "@TABSPEC@\n", t)
    t = re.sub(r"\{\\textwidth\}", "", t)
    t = t.replace(r"\arw{}", r"$\rightarrow$")
    # bold table headers we added
    t = re.sub(r"\\textbf\{([^}]*)\}", r"\1", t)
    # whitespace
    t = re.sub(r"[ \t]+", " ", t)
    return [ln.strip() for ln in t.split("\n") if ln.strip()]


a, b = normalise(old_body), normalise(new_body)
diff = [d for d in difflib.unified_diff(a, b, "original", "migrated", n=0)
        if d.startswith(("+", "-")) and not d.startswith(("+++", "---"))]

if not diff:
    print("IDENTICAL: prose, equations, algorithms and table data unchanged.")
else:
    print(f"{len(diff)} differing line(s):")
    for d in diff:
        print("  " + d[:200])

# independent invariants
for name, pat in [
    ("equations", r"\\begin\{(equation|align)\}"),
    ("algorithms", r"\\begin\{algorithm\}"),
    ("figures", r"\\includegraphics"),
    ("labels", r"\\label\{(fig|tab|alg|eq):"),
]:
    print(f"{name:12s} old={len(re.findall(pat, old))} new={len(re.findall(pat, new))}")

old_keys = set(re.findall(r"\\bibitem\{(ref[0-9]+)\}", old))
new_keys = set(re.findall(r"\\bibitem\{(ref[0-9]+)\}", new))
print(f"bib keys     identical={old_keys == new_keys} ({len(new_keys)} keys)")
cited = set()
for g in re.findall(r"\\citep\{([^}]*)\}", new):
    cited.update(g.split(","))
print(f"cited keys   all defined={cited <= new_keys}, uncited={sorted(new_keys - cited)}")
