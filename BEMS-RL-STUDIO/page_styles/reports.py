"""CSS dels informes HTML/PDF generats des de resultats."""

REPORT_HTML_CSS = """
<style>
  @page { size: A4; margin: 15mm 13mm; }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    background: #eef3f8;
    color: #17233c;
    font-family: "Segoe UI", Arial, sans-serif;
    line-height: 1.45;
  }
  .report-shell {
    max-width: 1120px;
    margin: 0 auto;
    padding: 22px;
    background: #ffffff;
  }
  .cover {
    padding: 30px 34px;
    border-radius: 14px;
    color: #ffffff;
    background: linear-gradient(135deg, #0f766e 0%, #1d4ed8 100%);
    page-break-inside: avoid;
  }
  .eyebrow {
    margin: 0 0 10px;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    opacity: 0.86;
  }
  h1 {
    margin: 0;
    font-size: 32px;
    line-height: 1.15;
    letter-spacing: 0;
  }
  .subtitle {
    max-width: 780px;
    margin: 12px 0 0;
    color: rgba(255, 255, 255, 0.88);
    font-size: 14px;
  }
  .summary-grid,
  .filter-strip,
  .kpi-row {
    display: flex;
    flex-wrap: wrap;
  }
  .summary-grid {
    margin: 22px -5px -5px 0;
  }
  .summary-item {
    width: 24%;
    min-height: 72px;
    margin: 0 5px 5px 0;
    padding: 12px 14px;
    border: 1px solid rgba(255, 255, 255, 0.24);
    border-radius: 8px;
    background: rgba(255, 255, 255, 0.12);
  }
  .summary-label {
    font-size: 11px;
    text-transform: uppercase;
    color: rgba(255, 255, 255, 0.72);
  }
  .summary-value {
    margin-top: 4px;
    font-size: 15px;
    font-weight: 700;
    overflow-wrap: anywhere;
  }
  .filter-strip {
    margin: 18px -8px 8px 0;
  }
  .filter-item {
    width: 24%;
    min-height: 70px;
    margin: 0 8px 8px 0;
    padding: 12px 14px;
    border: 1px solid #d7deeb;
    border-radius: 8px;
    background: #f8fbff;
  }
  .filter-label {
    color: #64748b;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
  }
  .filter-value {
    margin-top: 3px;
    font-size: 14px;
    font-weight: 700;
    color: #17233c;
  }
  .block-title {
    margin: 26px 0 12px;
    color: #17233c;
    font-size: 20px;
    line-height: 1.2;
  }
  .kpi-row {
    margin: 0 -12px 18px 0;
  }
  .kpi {
    width: 24%;
    min-height: 92px;
    margin: 0 12px 12px 0;
    border: 1px solid #d7deeb;
    border-radius: 8px;
    padding: 14px 16px;
    background: #ffffff;
    page-break-inside: avoid;
  }
  .kpi-val {
    color: #0f766e;
    font-size: 24px;
    font-weight: 800;
    line-height: 1.15;
  }
  .kpi-lbl {
    margin-top: 7px;
    color: #64748b;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.02em;
    text-transform: uppercase;
  }
  .report-section {
    margin-top: 28px;
  }
  .section-heading {
    margin: 0 0 12px;
    padding-left: 12px;
    border-left: 5px solid #0f766e;
    color: #17233c;
    font-size: 18px;
    font-weight: 800;
    line-height: 1.25;
    page-break-after: avoid;
  }
  .chart {
    margin: 0 0 20px;
    padding: 14px;
    border: 1px solid #d7deeb;
    border-radius: 8px;
    background: #ffffff;
    page-break-inside: avoid;
  }
  .chart h3 {
    margin: 0 0 10px;
    color: #17233c;
    font-size: 15px;
    line-height: 1.25;
  }
  .chart img {
    display: block;
    width: 100%;
    max-width: 100%;
    border: 0;
  }
  .chart .plotly-graph-div {
    width: 100% !important;
  }
  .empty-note {
    margin: 20px 0 0;
    padding: 14px 16px;
    border: 1px solid #d7deeb;
    border-radius: 8px;
    color: #64748b;
    background: #f8fbff;
  }
  @media print {
    body { background: #ffffff; }
    .report-shell { padding: 0; }
    .cover { border-radius: 0; }
  }
</style>
"""
