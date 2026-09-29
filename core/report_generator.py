from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4


def generate_pdf(row, filename):

    doc = SimpleDocTemplate(filename, pagesize=A4)

    styles = getSampleStyleSheet()
    content = []

    # =========================
    # TITLE
    # =========================

    content.append(
        Paragraph(
            "Anammox Reactor Simulation Report",
            styles["Title"]
        )
    )

    content.append(Spacer(1, 12))

    # =========================
    # BASIC RESULTS
    # =========================

    summary = f"""
    <b>Final NH4:</b> {row['final_nh4']:.3f}<br/>
    <b>Final NO2:</b> {row['final_no2']:.3f}<br/>
    <b>Final NO3:</b> {row['final_no3']:.3f}<br/>
    <b>Final Biomass:</b> {row['final_biomass']:.3f}<br/>
    <b>Performance index (model):</b> {row['stability']:.3f}<br/>
    """

    content.append(
        Paragraph(summary, styles["Normal"])
    )

    content.append(Spacer(1, 12))

    # =========================
    # SCIENTIFIC INTERPRETATION
    # =========================

    stability = row["stability"]

    stage = str(row.get("stage", "anammox") or "anammox")
    if stage == "pn":
        what = "nitrite accumulation ratio (NAR) predicted by the model"
    else:
        what = "predicted TIN removal relative to the autotrophic maximum (≈89 %)"
    if stability > 0.9:
        level = "close to the theoretical optimum"
    elif stability > 0.7:
        level = "moderately below the optimum"
    else:
        level = "well below the optimum — check operating conditions"
    interpretation = (f"The index ({stability:.2f}) is the {what}; it is {level}. "
                      "This is an uncalibrated model result, not a measured stability — "
                      "confirm with laboratory data (TIN removal, ΔNO3/ΔNH4).")

    content.append(
        Paragraph(
            "<b>Scientific Interpretation:</b><br/>" + interpretation,
            styles["Normal"]
        )
    )

    content.append(Spacer(1, 12))

    # =========================
    # CONCLUSION
    # =========================

    conclusion = """
    This report is generated based on a mechanistic Anammox model including:
    Monod kinetics, substrate inhibition, and environmental stress factors.
    """

    content.append(
        Paragraph(
            "<b>Conclusion:</b><br/>" + conclusion,
            styles["Normal"]
        )
    )

    doc.build(content)