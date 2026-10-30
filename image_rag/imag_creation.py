from fpdf import FPDF
import matplotlib.pyplot as plt

# 1. Generate a real line chart and save it as an image
plt.figure(figsize=(6, 3))
x_zones = ['US-East', 'EU-West', 'AP-South', 'SA-East']
latencies = [45, 62, 110, 85]

plt.plot(x_zones, latencies, marker='o', color='#00a8e8', linewidth=2, markersize=8)
plt.title('Q3 2026 System Latency (ms) by Availability Zone', fontsize=10, fontweight='bold')
plt.xlabel('Availability Zones', fontsize=8)
plt.ylabel('Latency (ms)', fontsize=8)
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()

chart_path = "real_latency_chart.png"
plt.savefig(chart_path, dpi=200)
plt.close()

# 2. Build the PDF containing text and the real chart image
pdf = FPDF()
pdf.add_page()
pdf.set_font("Helvetica", "B", 16)
pdf.cell(0, 10, "Quarterly Architecture & Infrastructure Review", ln=1)

pdf.set_font("Helvetica", "", 11)
pdf.multi_cell(
    0,
    6,
    "This document outlines the cloud infrastructure performance metrics for Q3"
    " 2026. Below is the system latency distribution chart across our"
    " primary availability zones.",
)
pdf.ln(10)

# Insert the real chart into the PDF
pdf.image(chart_path, x=15, y=50, w=150)

pdf.output("visual_document_with_chart.pdf")
print("Visual PDF with a real chart generated successfully!")
