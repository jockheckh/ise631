"""Rebuild IPR2 PDF pages as native PowerPoint text and shape objects.

The PDF is the layout reference; no slide-sized pictures are used. The TeX
source remains the authoritative source for formulas and wording.
"""

from __future__ import annotations

import io
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

import pymupdf


ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "reports/IPR2/IPR2_BRIEF.pdf"
TEMPLATE = ROOT / "reports/IPR2/IPR2_BRIEF.pptx"
OUTPUT = ROOT / "reports/IPR2/IPR2_BRIEF_EDITABLE.pptx"

P = "http://schemas.openxmlformats.org/presentationml/2006/main"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
REL = "http://schemas.openxmlformats.org/package/2006/relationships"
ET.register_namespace("p", P)
ET.register_namespace("a", A)
ET.register_namespace("r", R)

SLIDE_CX = 12192000
SLIDE_CY = 6858000

# Dense display equations remain exact PDF crops. All surrounding prose,
# headings, labels, table contents, rules, and status shapes are native objects.
MATH_REGIONS = {
    5: [(60, 132, 180, 173), (235, 137, 443, 160)],
    6: [(10, 53, 225, 112), (235, 59, 443, 111), (61, 135, 205, 150)],
    7: [(10, 53, 210, 116), (218, 48, 443, 120), (218, 128, 443, 145)],
    8: [(128, 36, 324, 66)],
    9: [(90, 50, 362, 72)],
    10: [(38, 62, 413, 100), (87, 150, 368, 181)],
    15: [(10, 43, 443, 88), (10, 99, 443, 143)],
    16: [(10, 44, 443, 78), (10, 85, 443, 118), (10, 122, 443, 154)],
    17: [(10, 48, 443, 115), (10, 129, 443, 166)],
    18: [(10, 48, 443, 86), (10, 91, 443, 117)],
    19: [(10, 58, 443, 83), (10, 83, 443, 129)],
    20: [(10, 35, 443, 82), (10, 83, 443, 118), (10, 120, 443, 183)],
    21: [(80, 51, 373, 73)],
    22: [(10, 50, 443, 111)],
}

TEXT_OVERRIDES = {
    8: [
        ((10, 69, 443, 160), [
            ((30, 71, 443, 82), "1. Affine LP versus exact MDP. Every feasible D1 function satisfies the Bellman inequalities.", 8.7),
            ((30, 82, 443, 94), "Backward induction bounds the exact value above. Restricting the value family cannot lower the minimum.", 8.7),
            ((30, 105, 443, 117), "2. Fluid LP versus affine LP. Map feasible P1 weights X to expected class acceptances Y.", 8.7),
            ((30, 117, 443, 129), "P1's moment equations give each class acceptance ≤ expected arrivals and AY ≤ c. The objectives agree.", 8.7),
            ((10, 141, 443, 153), "Structural result: if every c_i > 0 and every p_tj > 0, a nonincreasing optimal price trajectory exists.", 8.7),
            ((10, 153, 443, 164), "An arbitrary optimal solver output need not be monotone.", 8.7),
        ]),
    ],
    17: [
        ((10, 168, 443, 191), [
            ((10, 169, 443, 180), "x counts discounted visits weighted by the initial-state measure. Complementary slackness identifies optimal actions.", 8.4),
            ((10, 180, 443, 191), "With positive initial weight on every state, the minimizing value vector equals the optimal value everywhere.", 8.4),
        ]),
    ],
    18: [
        ((10, 119, 443, 153), [
            ((10, 120, 443, 132), "Each capacity shadow price is nonnegative. Complementary slackness characterizes primal-dual optima.", 8.4),
            ((10, 132, 443, 144), "An online rule accepts when fare covers the capacity shadow cost; its policy performance needs separate evaluation.", 8.4),
        ]),
    ],
    19: [
        ((10, 35, 443, 55), [
            ((10, 35, 443, 46), "At period 1, use only initial capacity c; in later periods use the full remaining-capacity state set.", 8.2),
            ((10, 46, 443, 56), "Terminal intercept and slopes are zero. Earlier affine coefficients are free. The program is", 8.2),
        ]),
    ],
    21: [
        ((10, 75, 443, 100), [
            ((10, 76, 443, 87), "The proof uses the first period with positive P1 support for a resource, complementary slackness,", 8.4),
            ((10, 87, 443, 98), "and price changes that preserve feasibility and optimality.", 8.4),
        ]),
        ((10, 103, 443, 124), [
            ((10, 104, 443, 115), "Why “exists” matters: Example 1 admits θ₂=0, b₂=0.5, θ₁=0.75, b₁=0, with objective 0.75.", 8.4),
            ((10, 115, 443, 126), "Here b₁ < b₂. Zero-demand and zero-capacity cases lie outside the theorem assumptions.", 8.4),
        ]),
    ],
    22: [
        ((10, 35, 443, 50), [
            ((10, 35, 443, 48), "For t>1, define w_j = p_tj(f_j − b_{t+1}ᵀA_j) and d_i = b_{t,i} − b_{t+1,i}. Pricing solves", 8.2),
        ]),
    ],
}

TABLES = {
    2: {
        "bbox": (9.9, 35.0, 443.6, 211.4),
        "columns": [0.23, 0.33, 0.17, 0.27],
        "font": 7.5,
        "rows": [
            ["Section", "Deliverable", "Status", "Next action"],
            ["1. Intro (I14)", "Pricing motivation and approved RQs", "Draft", "Verify history and prevalence"],
            ["2. RM (I01–I03)", "Discounted LP, exact MDP, fluid LP", "Draft", "Audit signs and example"],
            ["3. Method (I04–I06, I09)", "Affine ALP, duality, decision rule", "Draft", "Complete formal audit"],
            ["4. Proof (I07, I10)", "Bound hierarchy and theorem", "Draft", "File independent proof audit"],
            ["5. Scale (I11)", "Pricing and column generation", "Draft", "Verify complexity and separation"],
            ["6. Design (I08, I12)", "Benchmarks, metrics, policies", "Draft", "Approve factors and baselines"],
            ["6. Results (I08, I12)", "Code, tables, chart, sensitivity", "Not started", "Pass preflight and tests"],
            ["7. Critique (I13)", "Assumptions and alternatives", "Draft", "Link claims to evidence"],
            ["8. Literature (I14)", "Pricing lineage and FTC context", "Not started", "Verify works and primary source"],
            ["8. Extension (I14)", "Synthetic pricing application", "Blocked", "Await course and human gate"],
            ["9. Conclusion", "Three supported takeaways", "Draft", "Update after results"],
        ],
    },
    5: {
        "bbox": (9.9, 35.0, 443.6, 108.5),
        "columns": [0.21, 0.79], "font": 7.2,
        "rows": [
            ["Model element", "Definition"],
            ["State", "Period t ∈ {1,…,T}; remaining capacity r = (r_1,…,r_m), with each r_i ∈ {0,1,…,c_i}."],
            ["Arrival", "Class j arrives with probability p_tj. No arrival has probability 1 − Σ_j p_tj. At most one request arrives per period."],
            ["Action", "u_j ∈ {0,1} indicates whether class j would be accepted; a_ij u_j ≤ r_i for each resource and class."],
            ["Reward and next state", "Accepting class j earns f_j and moves to r − A_j; otherwise capacity remains r."],
        ],
    },
    9: {
        "bbox": (100, 76, 353, 130),
        "columns": [0.26, 0.12, 0.62], "font": 7.1,
        "rows": [
            ["Formulation", "Value", "Evidence status"],
            ["Exact MDP", "0.75", "Hand calculation; published example"],
            ["Affine LP (P1)", "0.75", "Published example; reproduction planned"],
            ["Fluid LP", "1.00", "Hand calculation; published example"],
        ],
    },
    11: {
        "bbox": (9.9, 35, 443.6, 130),
        "columns": [0.23, 0.77], "font": 7.0, "header": False,
        "rows": [
            ["Factors", "Resources, horizon, load, fare spread, arrival timing, and single- versus multi-resource products. Start with exactly enumerable cases."],
            ["Comparators", "Exact DP where tractable; fluid and certified affine bounds; fixed static and dynamic policies; separately labeled re-solving variants; proposed first-come feasible baseline."],
            ["Outcomes", "Bound gaps, exact or estimated policy reward, paired dynamic-minus-static difference, runtime, memory, iterations, and generated columns."],
            ["Inference", "Common arrival paths and predeclared seeds; report 95% intervals for each policy mean and paired difference. Use absolute gaps when exact value is zero."],
        ],
    },
    12: {
        "bbox": (9.9, 35, 443.6, 112),
        "columns": [0.30, 0.70], "font": 7.0,
        "rows": [
            ["Model assumption", "Question to test or disclose"],
            ["Known exogenous arrivals", "How sensitive are policies to misspecified probabilities?"],
            ["Nonreplenishing capacity", "Does the intended application have reusable assets?"],
            ["Affine value function", "How much state dependence is lost within one solve?"],
            ["Algorithm and scaling", "Which claims are proved, certified, or only observed on test instances?"],
            ["Published policy comparison", "How much gain comes from time prices, lookahead, or re-solving?"],
        ],
    },
    13: {
        "bbox": (9.9, 71, 443.6, 148),
        "columns": [0.27, 0.73], "font": 6.9,
        "rows": [
            ["Research thread", "Candidate references supplied for verification"],
            ["Customer choice and\nrelated methods", "Zhang and Adelman (2009); Barz et al. (2023); Hausenblas et al. (2025)"],
            ["Individualized pricing", "Jahandideh et al. (2020); Lei et al. (2023/2025)"],
            ["Parallel personalization line", "Acquisti and Varian (2005); Aydin and Ziya (2009); Ban and Keskin (2021)"],
            ["Policy context", "FTC inquiry (January 2025): consumer data in individualized pricing"],
        ],
    },
    14: {
        "bbox": (9.9, 35, 443.6, 110),
        "columns": [0.25, 0.75], "font": 7.0, "header": False,
        "rows": [
            ["Next evidence gate", "Source-linked proof notes; exact DP and LP agreement; fluid/static tests; full small affine LP; pricing versus exhaustive search; paired policy comparisons."],
            ["★ Proof (8)", "Is the theorem and LP treatment sufficient for the final brief?"],
            ["★ Algorithm (10)", "How much pricing and column generation must IPR 3 implement?"],
            ["★ Evidence (11)", "Which published result and comparison protocol should IPR 3 target?"],
            ["★ Application (13)", "Is a conceptual, source-checked connection sufficient?"],
        ],
    },
    23: {
        "bbox": (9.9, 35, 443.6, 116),
        "columns": [0.20, 0.27, 0.53], "font": 6.8,
        "rows": [
            ["Block", "Variation", "Evidence to record"],
            ["Verification", "Example 1; two-resource case; edge cases", "DP, exact LP and dual, fluid, full affine LP; values and residuals"],
            ["Bound strength", "Size, load, timing, fare", "Exact V* when feasible; fluid and certified affine bounds"],
            ["Policy value", "Fixed and re-solved policies", "Tiny-case exact value; policy and paired-difference 95% intervals"],
            ["Computation", "Enumeration versus columns", "Runtime, memory, iterations, generated columns, pricing gaps"],
            ["Truncation", "Columns, states, horizon", "Time saved, omitted constraints, surviving certificates"],
        ],
    },
    24: {
        "bbox": (9.9, 35, 443.6, 132),
        "columns": [0.10, 0.17, 0.18, 0.55], "font": 7.0,
        "rows": [
            ["ID", "Final part", "Register", "Evidence needed next"],
            ["I01", "2–4", "Planned", "Discounted Bellman LP, occupancy dual, complementary slackness audit"],
            ["I02", "2", "Planned", "Exact network MDP and state-growth analysis"],
            ["I03", "2–3", "Planned", "Fluid primal/dual and static-policy validation"],
            ["I04", "3–5", "Planned", "Source-matched affine ALP and algorithm audit"],
            ["I05", "3", "Planned", "Paper method and solution approach, source-linked"],
            ["I06", "3–5", "Planned", "Correct LP course-concept mapping"],
            ["I07", "4", "Planned", "Principal theorem and independently reviewed proof"],
        ],
    },
    25: {
        "bbox": (9.9, 35, 443.6, 123),
        "columns": [0.10, 0.17, 0.18, 0.55], "font": 7.0,
        "rows": [
            ["ID", "Final part", "Register", "Evidence needed next"],
            ["I08", "6", "Planned", "Reproducible fluid, static, and dynamic policy tests"],
            ["I09", "3–4", "Planned", "Approximation benefit with verified example"],
            ["I10", "4", "Planned", "Full bound-dominance derivation and audit"],
            ["I11", "5", "Planned", "Pricing formulation and qualified complexity account"],
            ["I12", "6", "Planned", "Policy, exact MDP, and fluid gap results"],
            ["I13", "7", "Planned", "Evidence-based critique and alternatives"],
            ["I14", "1, 5, 8", "Planned", "Approved independent RQs linked to final analysis"],
        ],
    },
}


def tag(ns: str, local: str) -> str:
    return f"{{{ns}}}{local}"


def rgb(value: int | tuple[float, float, float]) -> str:
    if isinstance(value, int):
        return f"{value:06X}"
    return "".join(f"{round(v * 255):02X}" for v in value)


def xywh(bbox, sx: float, sy: float, pad_pt: float = 0):
    x0, y0, x1, y1 = bbox
    return (
        round(x0 * sx),
        round(y0 * sy),
        max(1, round((x1 - x0) * sx + pad_pt * 12700)),
        max(1, round((y1 - y0) * sy + pad_pt * 12700)),
    )


def transform(parent, bbox, sx, sy, pad_pt=0):
    x, y, w, h = xywh(bbox, sx, sy, pad_pt)
    xf = ET.SubElement(parent, tag(A, "xfrm"))
    ET.SubElement(xf, tag(A, "off"), {"x": str(x), "y": str(y)})
    ET.SubElement(xf, tag(A, "ext"), {"cx": str(w), "cy": str(h)})


def native_text(tree, shape_id, span, sx, sy, font_scale):
    raw = span["text"].replace("\ufe00", "").replace("\ufe01", "")
    raw = raw.replace("\ufe02", "").replace("\ufe03", "")
    if not raw.strip():
        return False
    sp = ET.SubElement(tree, tag(P, "sp"))
    nv = ET.SubElement(sp, tag(P, "nvSpPr"))
    ET.SubElement(nv, tag(P, "cNvPr"), {"id": str(shape_id), "name": f"Editable text {shape_id}"})
    ET.SubElement(nv, tag(P, "cNvSpPr"), {"txBox": "1"})
    ET.SubElement(nv, tag(P, "nvPr"))
    pr = ET.SubElement(sp, tag(P, "spPr"))
    transform(pr, span["bbox"], sx, sy, 2.5)
    ET.SubElement(ET.SubElement(pr, tag(A, "prstGeom"), {"prst": "rect"}), tag(A, "avLst"))
    ET.SubElement(pr, tag(A, "noFill"))
    ET.SubElement(ET.SubElement(pr, tag(A, "ln")), tag(A, "noFill"))
    tx = ET.SubElement(sp, tag(P, "txBody"))
    ET.SubElement(tx, tag(A, "bodyPr"), {"wrap": "none", "lIns": "0", "tIns": "0", "rIns": "0", "bIns": "0", "anchor": "t"})
    ET.SubElement(tx, tag(A, "lstStyle"))
    paragraph = ET.SubElement(tx, tag(A, "p"))
    ET.SubElement(paragraph, tag(A, "pPr"), {"algn": "l"})
    run = ET.SubElement(paragraph, tag(A, "r"))
    font = span["font"]
    math = "Math" in font or font.startswith("MS")
    props = {"lang": "en-US", "sz": str(max(600, round(span["size"] * font_scale * 100)))}
    if "Bold" in font:
        props["b"] = "1"
    if "Oblique" in font or "Italic" in font:
        props["i"] = "1"
    rp = ET.SubElement(run, tag(A, "rPr"), props)
    ET.SubElement(ET.SubElement(rp, tag(A, "solidFill")), tag(A, "srgbClr"), {"val": rgb(span["color"])})
    ET.SubElement(rp, tag(A, "latin"), {"typeface": "Cambria Math" if math else "Arial"})
    ET.SubElement(run, tag(A, "t"), {"{http://www.w3.org/XML/1998/namespace}space": "preserve"}).text = raw
    ET.SubElement(paragraph, tag(A, "endParaRPr"), {"lang": "en-US"})
    return True


def native_rect(tree, shape_id, bbox, fill, sx, sy):
    sp = ET.SubElement(tree, tag(P, "sp"))
    nv = ET.SubElement(sp, tag(P, "nvSpPr"))
    ET.SubElement(nv, tag(P, "cNvPr"), {"id": str(shape_id), "name": f"Editable rectangle {shape_id}"})
    ET.SubElement(nv, tag(P, "cNvSpPr"))
    ET.SubElement(nv, tag(P, "nvPr"))
    pr = ET.SubElement(sp, tag(P, "spPr"))
    transform(pr, bbox, sx, sy)
    ET.SubElement(ET.SubElement(pr, tag(A, "prstGeom"), {"prst": "rect"}), tag(A, "avLst"))
    ET.SubElement(ET.SubElement(pr, tag(A, "solidFill")), tag(A, "srgbClr"), {"val": rgb(fill)})
    ET.SubElement(ET.SubElement(pr, tag(A, "ln")), tag(A, "noFill"))


def native_picture(tree, shape_id, bbox, sx, sy, rel_id):
    pic = ET.SubElement(tree, tag(P, "pic"))
    nv = ET.SubElement(pic, tag(P, "nvPicPr"))
    ET.SubElement(nv, tag(P, "cNvPr"), {"id": str(shape_id), "name": f"Equation {shape_id}"})
    ET.SubElement(nv, tag(P, "cNvPicPr"))
    ET.SubElement(nv, tag(P, "nvPr"))
    fill = ET.SubElement(pic, tag(P, "blipFill"))
    ET.SubElement(fill, tag(A, "blip"), {tag(R, "embed"): rel_id})
    ET.SubElement(ET.SubElement(fill, tag(A, "stretch")), tag(A, "fillRect"))
    pr = ET.SubElement(pic, tag(P, "spPr"))
    transform(pr, bbox, sx, sy)
    ET.SubElement(ET.SubElement(pr, tag(A, "prstGeom"), {"prst": "rect"}), tag(A, "avLst"))


def native_table(tree, shape_id, spec, sx, sy, font_scale):
    bbox = spec["bbox"]
    x, y, w, h = xywh(bbox, sx, sy)
    frame = ET.SubElement(tree, tag(P, "graphicFrame"))
    nv = ET.SubElement(frame, tag(P, "nvGraphicFramePr"))
    ET.SubElement(nv, tag(P, "cNvPr"), {"id": str(shape_id), "name": f"Editable table {shape_id}"})
    ET.SubElement(nv, tag(P, "cNvGraphicFramePr"))
    ET.SubElement(nv, tag(P, "nvPr"))
    xf = ET.SubElement(frame, tag(P, "xfrm"))
    ET.SubElement(xf, tag(A, "off"), {"x": str(x), "y": str(y)})
    ET.SubElement(xf, tag(A, "ext"), {"cx": str(w), "cy": str(h)})
    graphic = ET.SubElement(frame, tag(A, "graphic"))
    data = ET.SubElement(graphic, tag(A, "graphicData"), {"uri": "http://schemas.openxmlformats.org/drawingml/2006/table"})
    table = ET.SubElement(data, tag(A, "tbl"))
    ET.SubElement(table, tag(A, "tblPr"), {"firstRow": "1"})
    grid = ET.SubElement(table, tag(A, "tblGrid"))
    widths = [round(w * part) for part in spec["columns"]]
    widths[-1] = w - sum(widths[:-1])
    for width in widths:
        ET.SubElement(grid, tag(A, "gridCol"), {"w": str(width)})
    rows = spec["rows"]
    height = round(h / len(rows))
    for ri, cells in enumerate(rows):
        tr = ET.SubElement(table, tag(A, "tr"), {"h": str(height if ri < len(rows)-1 else h-height*(len(rows)-1))})
        for ci, value in enumerate(cells):
            tc = ET.SubElement(tr, tag(A, "tc"))
            tx = ET.SubElement(tc, tag(A, "txBody"))
            ET.SubElement(tx, tag(A, "bodyPr"), {"wrap": "square", "lIns": "0", "rIns": "0", "tIns": "0", "bIns": "0", "anchor": "ctr"})
            ET.SubElement(tx, tag(A, "lstStyle"))
            para = ET.SubElement(tx, tag(A, "p"))
            props = {"lang": "en-US", "sz": str(round(spec["font"] * font_scale * 100))}
            if ri == 0 and spec.get("header", True):
                props["b"] = "1"
            for line_index, line_text in enumerate(value.split("\n")):
                if line_index:
                    ET.SubElement(para, tag(A, "br"))
                run = ET.SubElement(para, tag(A, "r"))
                rp = ET.SubElement(run, tag(A, "rPr"), props)
                color = "FFFFFF" if ci == 2 and value == "Blocked" else "000000"
                ET.SubElement(ET.SubElement(rp, tag(A, "solidFill")), tag(A, "srgbClr"), {"val": color})
                ET.SubElement(rp, tag(A, "latin"), {"typeface": "Arial"})
                ET.SubElement(run, tag(A, "t")).text = line_text
            ET.SubElement(para, tag(A, "endParaRPr"), {"lang": "en-US"})
            tcp = ET.SubElement(tc, tag(A, "tcPr"), {"marL": "10000", "marR": "10000", "marT": "0", "marB": "0"})
            fill_color = "FFFFFF"
            if ci == 2:
                fill_color = {"Draft": "FFE769", "Not started": "EEAE36", "Blocked": "A6252B"}.get(value, "FFFFFF")
            ET.SubElement(ET.SubElement(tcp, tag(A, "solidFill")), tag(A, "srgbClr"), {"val": fill_color})
            bottom = ET.SubElement(tcp, tag(A, "lnB"), {"w": "6350"})
            ET.SubElement(ET.SubElement(bottom, tag(A, "solidFill")), tag(A, "srgbClr"), {"val": "333333"})


def math_regions_for_page(page, number):
    lines = [pymupdf.Rect(line["bbox"])
             for block in page.get_text("dict")["blocks"] if block["type"] == 0
             for line in block["lines"]]
    regions = []
    for raw in MATH_REGIONS.get(number, []):
        region = pymupdf.Rect(*raw)
        changed = True
        while changed:
            changed = False
            for line in lines:
                intersection = region & line
                if intersection.is_empty or intersection.width < 0.8 or intersection.height < 0.8:
                    continue
                expanded = region | line
                if expanded != region:
                    region = expanded
                    changed = True
        regions.append(region + (-0.5, -0.5, 0.5, 0.5))
    merged = []
    for region in regions:
        if merged and merged[-1].intersects(region):
            merged[-1] = merged[-1] | region
        else:
            merged.append(region)
    return [r & page.rect for r in merged]


def make_slide(page, number):
    sx = SLIDE_CX / page.rect.width
    sy = SLIDE_CY / page.rect.height
    font_scale = (SLIDE_CX / 12700) / page.rect.width
    slide = ET.Element(tag(P, "sld"))
    csld = ET.SubElement(slide, tag(P, "cSld"))
    tree = ET.SubElement(csld, tag(P, "spTree"))
    nv = ET.SubElement(tree, tag(P, "nvGrpSpPr"))
    ET.SubElement(nv, tag(P, "cNvPr"), {"id": "1", "name": ""})
    ET.SubElement(nv, tag(P, "cNvGrpSpPr"))
    ET.SubElement(nv, tag(P, "nvPr"))
    grp = ET.SubElement(tree, tag(P, "grpSpPr"))
    xf = ET.SubElement(grp, tag(A, "xfrm"))
    for name in ("off", "chOff"):
        ET.SubElement(xf, tag(A, name), {"x": "0", "y": "0"})
    for name in ("ext", "chExt"):
        ET.SubElement(xf, tag(A, name), {"cx": "0", "cy": "0"})

    sid = 2
    table_spec = TABLES.get(number)
    table_region = pymupdf.Rect(table_spec["bbox"]) if table_spec else None
    for drawing in page.get_drawings():
        if table_region is not None and table_region.contains(drawing["rect"].tl):
            continue
        if drawing["type"] == "f" and drawing["fill"] is not None:
            for item in drawing["items"]:
                if item[0] == "re":
                    box = item[1]
                    if box.width >= page.rect.width - 1 and box.height >= page.rect.height - 1:
                        continue
                    native_rect(tree, sid, box, drawing["fill"], sx, sy)
                    sid += 1
        elif drawing["type"] == "s" and drawing["color"] is not None:
            for item in drawing["items"]:
                if item[0] == "l":
                    p0, p1 = item[1], item[2]
                    width = max(drawing["width"] or 0.4, 0.3)
                    if abs(p0.y - p1.y) < 0.02:
                        bbox = (min(p0.x, p1.x), p0.y, max(p0.x, p1.x), p0.y + width)
                    elif abs(p0.x - p1.x) < 0.02:
                        bbox = (p0.x, min(p0.y, p1.y), p0.x + width, max(p0.y, p1.y))
                    else:
                        continue
                    native_rect(tree, sid, bbox, drawing["color"], sx, sy)
                    sid += 1

    regions = math_regions_for_page(page, number)
    overrides = [(pymupdf.Rect(area), lines) for area, lines in TEXT_OVERRIDES.get(number, [])]
    for block in page.get_text("dict")["blocks"]:
        if block["type"] != 0:
            continue
        for line in block["lines"]:
            center = pymupdf.Rect(line["bbox"]).tl + (pymupdf.Rect(line["bbox"]).br - pymupdf.Rect(line["bbox"]).tl) * 0.5
            if table_region is not None and table_region.contains(center):
                continue
            if any(area.intersects(pymupdf.Rect(line["bbox"])) for area, _ in overrides):
                continue
            if any(region.intersects(pymupdf.Rect(line["bbox"])) for region in regions):
                continue
            spans = [s for s in line["spans"] if s["text"].strip()]
            if not spans:
                continue
            plain = "".join(s["text"] for s in line["spans"])
            body = [s for s in spans if "Math" not in s["font"]]
            representative = max(body or spans, key=lambda s: len(s["text"]))
            combined = dict(representative)
            combined["text"] = plain
            combined["bbox"] = line["bbox"]
            if native_text(tree, sid, combined, sx, sy, font_scale):
                sid += 1

    for _, lines in overrides:
        for bbox, value, size in lines:
            span = {"text": value, "bbox": bbox, "font": "LMSans9-Regular", "size": size, "color": 0}
            if native_text(tree, sid, span, sx, sy, font_scale):
                sid += 1

    if table_spec:
        native_table(tree, sid, table_spec, sx, sy, font_scale)
        sid += 1

    pictures = {}
    for i, region in enumerate(regions, 1):
        rel_id = f"rId{i + 1}"
        name = f"equation_{number}_{i}.png"
        pix = page.get_pixmap(matrix=pymupdf.Matrix(4, 4), clip=region, alpha=False)
        pictures[name] = (rel_id, pix.tobytes("png"))
        native_picture(tree, sid, region, sx, sy, rel_id)
        sid += 1

    ET.SubElement(ET.SubElement(slide, tag(P, "clrMapOvr")), tag(A, "masterClrMapping"))
    return ET.tostring(slide, encoding="utf-8", xml_declaration=True), sid - 2, pictures


def main():
    doc = pymupdf.open(PDF)
    assert len(doc) == 25
    rendered = {}
    all_pictures = {}
    for number, page in enumerate(doc, 1):
        xml, count, pictures = make_slide(page, number)
        rendered[number] = xml
        all_pictures[number] = pictures
        print(f"slide {number}: {count} editable objects")
    with zipfile.ZipFile(TEMPLATE) as original, zipfile.ZipFile(OUTPUT, "w", zipfile.ZIP_DEFLATED) as result:
        for item in original.infolist():
            name = item.filename
            if name.startswith("ppt/media/"):
                continue
            match = re.fullmatch(r"ppt/slides/slide(\d+)\.xml", name)
            if match:
                number = int(match.group(1))
                result.writestr(name, rendered[number])
            elif re.fullmatch(r"ppt/slides/_rels/slide\d+\.xml\.rels", name):
                number = int(re.search(r"slide(\d+)", name).group(1))
                rels = ET.Element(tag(REL, "Relationships"))
                ET.SubElement(rels, tag(REL, "Relationship"), {
                    "Id": "rId1",
                    "Type": "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout",
                    "Target": "../slideLayouts/slideLayout7.xml",
                })
                for picture_name, (rel_id, _) in all_pictures.get(number, {}).items():
                    ET.SubElement(rels, tag(REL, "Relationship"), {
                        "Id": rel_id,
                        "Type": "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image",
                        "Target": f"../media/{picture_name}",
                    })
                result.writestr(name, ET.tostring(rels, encoding="utf-8", xml_declaration=True))
            else:
                result.writestr(item, original.read(name))
        for pictures in all_pictures.values():
            for picture_name, (_, data) in pictures.items():
                result.writestr(f"ppt/media/{picture_name}", data)
    print(OUTPUT)


if __name__ == "__main__":
    main()
