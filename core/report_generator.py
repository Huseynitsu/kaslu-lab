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
    <b>Stability:</b> {row['stability']:.3f}<br/>
    """

    content.append(
        Paragraph(summary, styles["Normal"])
    )

    content.append(Spacer(1, 12))

    # =========================
    # SCIENTIFIC INTERPRETATION
    # =========================

    stability = row["stability"]

    if stability > 0.9:
        interpretation = "Reactor shows HIGH stability and optimal Anammox performance."
    elif stability > 0.7:
        interpretation = "Reactor is moderately stable with some inhibitory conditions."
    else:
        interpretation = "Reactor is unstable and microbial activity is significantly inhibited."

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