import os
import svgwrite
from PIL import Image, ImageDraw, ImageFont

def ensure_dirs():
    os.makedirs("docs/flow-diagram", exist_ok=True)
    os.makedirs("docs/architecture", exist_ok=True)

def generate_flow_diagram():
    ensure_dirs()
    svg_path = "docs/flow-diagram/flow_diagram.svg"
    png_path = "docs/flow-diagram/flow_diagram.png"
    
    dwg = svgwrite.Drawing(svg_path, size=(1200, 750), profile='full')
    
    # Styles & Colors
    dwg.add(dwg.style("""
        .title { font-family: 'Segoe UI', Arial, sans-serif; font-size: 24px; font-weight: bold; fill: #0f172a; }
        .subtitle { font-family: 'Segoe UI', Arial, sans-serif; font-size: 14px; fill: #64748b; }
        .node-rect { fill: #ffffff; stroke: #0d9488; stroke-width: 2px; rx: 10px; ry: 10px; filter: drop-shadow(0px 4px 6px rgba(0,0,0,0.1)); }
        .node-rect-start { fill: #0d9488; stroke: #0f766e; stroke-width: 2px; rx: 12px; ry: 12px; }
        .node-rect-end { fill: #4f46e5; stroke: #4338ca; stroke-width: 2px; rx: 12px; ry: 12px; }
        .node-text { font-family: 'Segoe UI', Arial, sans-serif; font-size: 13px; font-weight: 600; fill: #1e293b; text-anchor: middle; }
        .node-text-light { font-family: 'Segoe UI', Arial, sans-serif; font-size: 13px; font-weight: 600; fill: #ffffff; text-anchor: middle; }
        .arrow { stroke: #0d9488; stroke-width: 2.5px; marker-end: url(#arrowhead); }
    """))

    # Marker
    marker = dwg.marker(id='arrowhead', insert=(10, 5), size=(10, 10), orient='auto')
    marker.add(dwg.path(d='M 0 0 L 10 5 L 0 10 z', fill='#0d9488'))
    dwg.defs.add(marker)

    # Background
    dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), fill='#f8fafc'))
    
    # Header
    dwg.add(dwg.text("System Flow Diagram - AI Career Intelligence Platform", insert=(50, 45), class_="title"))
    dwg.add(dwg.text("End-to-End User Journey, 2FA Verification, NLP Engine Execution & Re-Analysis Flow", insert=(50, 70), class_="subtitle"))

    steps = [
        ("1. User Login", "node-rect-start", True),
        ("2. 2FA Verification", "node-rect", False),
        ("3. Upload Resume", "node-rect", False),
        ("4. Upload Job Description", "node-rect", False),
        ("5. Text Extraction", "node-rect", False),
        ("6. NLP Processing", "node-rect", False),
        ("7. ATS Analysis", "node-rect", False),
        ("8. Job Matching", "node-rect", False),
        ("9. Skill Gap Detection", "node-rect", False),
        ("10. AI Recommendation", "node-rect", False),
        ("11. Job Readiness Score", "node-rect", False),
        ("12. Dashboard", "node-rect", False),
        ("13. Re-analysis", "node-rect-end", True)
    ]

    # Grid positioning: 4 columns x 4 rows
    col_w, row_h = 240, 130
    start_x, start_y = 60, 120

    coords = []
    for idx, (label, style_cls, is_highlight) in enumerate(steps):
        row = idx // 4
        col = idx % 4
        
        # Zigzag layout direction
        if row % 2 == 1:
            col = 3 - col
            
        x = start_x + col * col_w
        y = start_y + row * row_h
        coords.append((x, y, label, style_cls, is_highlight))

        box_w, box_h = 190, 60
        rect_cls = "node-rect-start" if idx == 0 else ("node-rect-end" if idx == 12 else "node-rect")
        dwg.add(dwg.rect(insert=(x, y), size=(box_w, box_h), class_=rect_cls))
        
        text_cls = "node-text-light" if is_highlight else "node-text"
        dwg.add(dwg.text(label, insert=(x + box_w/2, y + box_h/2 + 5), class_=text_cls))

    # Connect arrows
    for i in range(len(coords) - 1):
        x1, y1, _, _, _ = coords[i]
        x2, y2, _, _, _ = coords[i+1]
        
        box_w, box_h = 190, 60
        
        if y1 == y2:
            if x2 > x1:
                start_p = (x1 + box_w, y1 + box_h/2)
                end_p = (x2, y2 + box_h/2)
            else:
                start_p = (x1, y1 + box_h/2)
                end_p = (x2 + box_w, y2 + box_h/2)
        else:
            start_p = (x1 + box_w/2, y1 + box_h)
            end_p = (x2 + box_w/2, y2)
            
        dwg.add(dwg.line(start=start_p, end=end_p, class_="arrow"))

    dwg.save()
    print(f"[Diagram] Generated SVG flow diagram: {svg_path}")

    # Generate PNG using Pillow canvas rendering for crisp image output
    img_w, img_h = 1200, 750
    img = Image.new("RGB", (img_w, img_h), "#f8fafc")
    draw = ImageDraw.Draw(img)

    try:
        font_title = ImageFont.truetype("arial.ttf", 22)
        font_node = ImageFont.truetype("arial.ttf", 13)
    except Exception:
        font_title = ImageFont.load_default()
        font_node = ImageFont.load_default()

    draw.text((50, 30), "System Flow Diagram - AI Career Intelligence Platform", fill="#0f172a", font=font_title)
    
    for i in range(len(coords) - 1):
        x1, y1, _, _, _ = coords[i]
        x2, y2, _, _, _ = coords[i+1]
        box_w, box_h = 190, 60
        if y1 == y2:
            if x2 > x1:
                sp = (x1 + box_w, y1 + box_h/2)
                ep = (x2, y2 + box_h/2)
            else:
                sp = (x1, y1 + box_h/2)
                ep = (x2 + box_w, y2 + box_h/2)
        else:
            sp = (x1 + box_w/2, y1 + box_h)
            ep = (x2 + box_w/2, y2)
        draw.line([sp, ep], fill="#0d9488", width=3)

    for idx, (x, y, label, _, is_hl) in enumerate(coords):
        box_w, box_h = 190, 60
        bg_color = "#0d9488" if idx == 0 else ("#4f46e5" if idx == 12 else "#ffffff")
        outline = "#0f766e" if idx == 0 else ("#4338ca" if idx == 12 else "#0d9488")
        txt_color = "#ffffff" if is_hl else "#1e293b"
        
        draw.rounded_rectangle([x, y, x + box_w, y + box_h], radius=10, fill=bg_color, outline=outline, width=2)
        draw.text((x + 15, y + 20), label, fill=txt_color, font=font_node)

    img.save(png_path)
    print(f"[Diagram] Generated PNG flow diagram: {png_path}")

def generate_architecture_diagram():
    ensure_dirs()
    svg_path = "docs/architecture/architecture.svg"
    png_path = "docs/architecture/architecture.png"
    
    dwg = svgwrite.Drawing(svg_path, size=(1100, 700), profile='full')
    
    dwg.add(dwg.style("""
        .title { font-family: 'Segoe UI', Arial, sans-serif; font-size: 24px; font-weight: bold; fill: #0f172a; }
        .subtitle { font-family: 'Segoe UI', Arial, sans-serif; font-size: 14px; fill: #64748b; }
        .layer-box { fill: #f1f5f9; stroke: #cbd5e1; stroke-width: 2px; rx: 12px; }
        .comp-box { fill: #ffffff; stroke: #0d9488; stroke-width: 2px; rx: 8px; filter: drop-shadow(0px 2px 4px rgba(0,0,0,0.05)); }
        .db-box { fill: #fef3c7; stroke: #d97706; stroke-width: 2px; rx: 8px; }
        .comp-title { font-family: 'Segoe UI', Arial, sans-serif; font-size: 13px; font-weight: bold; fill: #0f172a; text-anchor: middle; }
        .layer-title { font-family: 'Segoe UI', Arial, sans-serif; font-size: 16px; font-weight: bold; fill: #334155; }
        .arrow { stroke: #0284c7; stroke-width: 2.5px; marker-end: url(#arch-arrow); }
    """))

    marker = dwg.marker(id='arch-arrow', insert=(10, 5), size=(10, 10), orient='auto')
    marker.add(dwg.path(d='M 0 0 L 10 5 L 0 10 z', fill='#0284c7'))
    dwg.defs.add(marker)

    dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), fill='#f8fafc'))
    
    dwg.add(dwg.text("System Architecture Diagram - Production Stack", insert=(50, 45), class_="title"))
    dwg.add(dwg.text("Frontend, Flask REST API & WebSocket Server, Business Services, Security & MongoDB Storage", insert=(50, 70), class_="subtitle"))

    # Layer 1: Frontend
    dwg.add(dwg.rect(insert=(50, 110), size=(1000, 100), class_="layer-box"))
    dwg.add(dwg.text("FRONTEND PRESENTATION LAYER", insert=(70, 135), class_="layer-title"))
    dwg.add(dwg.rect(insert=(280, 130), size=(200, 60), class_="comp-box"))
    dwg.add(dwg.text("HTML5 / CSS3 / JS UI", insert=(380, 165), class_="comp-title"))
    dwg.add(dwg.rect(insert=(510, 130), size=(200, 60), class_="comp-box"))
    dwg.add(dwg.text("Chart.js Dashboard", insert=(610, 165), class_="comp-title"))
    dwg.add(dwg.rect(insert=(740, 130), size=(200, 60), class_="comp-box"))
    dwg.add(dwg.text("SocketIO Client", insert=(840, 165), class_="comp-title"))

    # Layer 2: Flask Backend Routes & Middleware
    dwg.add(dwg.rect(insert=(50, 250), size=(1000, 110), class_="layer-box"))
    dwg.add(dwg.text("FLASK BACKEND & ROUTING LAYER", insert=(70, 275), class_="layer-title"))
    dwg.add(dwg.rect(insert=(280, 280), size=(180, 60), class_="comp-box"))
    dwg.add(dwg.text("REST API Blueprints", insert=(370, 315), class_="comp-title"))
    dwg.add(dwg.rect(insert=(480, 280), size=(180, 60), class_="comp-box"))
    dwg.add(dwg.text("Flask-SocketIO Engine", insert=(570, 315), class_="comp-title"))
    dwg.add(dwg.rect(insert=(680, 280), size=(180, 60), class_="comp-box"))
    dwg.add(dwg.text("Flask-Login & 2FA Middleware", insert=(770, 315), class_="comp-title"))

    # Layer 3: Services & Engines
    dwg.add(dwg.rect(insert=(50, 400), size=(1000, 140), class_="layer-box"))
    dwg.add(dwg.text("BUSINESS LOGIC & NLP ENGINES", insert=(70, 425), class_="layer-title"))
    
    services = ["Resume Parser", "NLP & Skill Engine", "ATS & Gap Matcher", "AI Rec Engine", "PyOTP 2FA Auth"]
    for i, s in enumerate(services):
        x = 70 + i * 185
        dwg.add(dwg.rect(insert=(x, 450), size=(170, 65), class_="comp-box"))
        dwg.add(dwg.text(s, insert=(x + 85, 488), class_="comp-title"))

    # Layer 4: Storage
    dwg.add(dwg.rect(insert=(50, 570), size=(1000, 100), class_="layer-box"))
    dwg.add(dwg.text("DATA & PERSISTENCE LAYER", insert=(70, 595), class_="layer-title"))
    dwg.add(dwg.rect(insert=(350, 590), size=(250, 60), class_="db-box"))
    dwg.add(dwg.text("MongoDB (PyMongo / JSON Store)", insert=(475, 625), class_="comp-title"))
    dwg.add(dwg.rect(insert=(630, 590), size=(250, 60), class_="comp-box"))
    dwg.add(dwg.text("Uploads Temp Storage", insert=(755, 625), class_="comp-title"))

    # Connections
    dwg.add(dwg.line(start=(610, 210), end=(610, 250), class_="arrow"))
    dwg.add(dwg.line(start=(550, 360), end=(550, 400), class_="arrow"))
    dwg.add(dwg.line(start=(550, 540), end=(550, 570), class_="arrow"))

    dwg.save()
    print(f"[Diagram] Generated SVG architecture diagram: {svg_path}")

    # Generate PNG using Pillow
    img_w, img_h = 1100, 700
    img = Image.new("RGB", (img_w, img_h), "#f8fafc")
    draw = ImageDraw.Draw(img)

    try:
        font_title = ImageFont.truetype("arial.ttf", 22)
        font_layer = ImageFont.truetype("arial.ttf", 15)
        font_comp = ImageFont.truetype("arial.ttf", 12)
    except Exception:
        font_title = ImageFont.load_default()
        font_layer = ImageFont.load_default()
        font_comp = ImageFont.load_default()

    draw.text((50, 30), "System Architecture Diagram - Production Stack", fill="#0f172a", font=font_title)

    # Layers
    draw.rounded_rectangle([50, 110, 1050, 210], radius=12, fill="#f1f5f9", outline="#cbd5e1", width=2)
    draw.text((70, 125), "FRONTEND PRESENTATION LAYER", fill="#334155", font=font_layer)
    draw.rounded_rectangle([280, 140, 480, 195], radius=8, fill="#ffffff", outline="#0d9488", width=2)
    draw.text((310, 160), "HTML5 / CSS3 / JS UI", fill="#0f172a", font=font_comp)
    draw.rounded_rectangle([510, 140, 710, 195], radius=8, fill="#ffffff", outline="#0d9488", width=2)
    draw.text((540, 160), "Chart.js Dashboard", fill="#0f172a", font=font_comp)
    draw.rounded_rectangle([740, 140, 940, 195], radius=8, fill="#ffffff", outline="#0d9488", width=2)
    draw.text((770, 160), "SocketIO Client", fill="#0f172a", font=font_comp)

    draw.rounded_rectangle([50, 240, 1050, 350], radius=12, fill="#f1f5f9", outline="#cbd5e1", width=2)
    draw.text((70, 255), "FLASK BACKEND & ROUTING LAYER", fill="#334155", font=font_layer)
    draw.rounded_rectangle([280, 275, 460, 330], radius=8, fill="#ffffff", outline="#0d9488", width=2)
    draw.text((300, 295), "REST API Blueprints", fill="#0f172a", font=font_comp)
    draw.rounded_rectangle([480, 275, 660, 330], radius=8, fill="#ffffff", outline="#0d9488", width=2)
    draw.text((500, 295), "Flask-SocketIO Engine", fill="#0f172a", font=font_comp)
    draw.rounded_rectangle([680, 275, 860, 330], radius=8, fill="#ffffff", outline="#0d9488", width=2)
    draw.text((695, 295), "Flask-Login & 2FA", fill="#0f172a", font=font_comp)

    draw.rounded_rectangle([50, 380, 1050, 520], radius=12, fill="#f1f5f9", outline="#cbd5e1", width=2)
    draw.text((70, 395), "BUSINESS LOGIC & NLP ENGINES", fill="#334155", font=font_layer)
    for i, s in enumerate(services):
        x = 70 + i * 185
        draw.rounded_rectangle([x, 425, x + 170, 490], radius=8, fill="#ffffff", outline="#0d9488", width=2)
        draw.text((x + 15, 450), s, fill="#0f172a", font=font_comp)

    draw.rounded_rectangle([50, 550, 1050, 660], radius=12, fill="#f1f5f9", outline="#cbd5e1", width=2)
    draw.text((70, 565), "DATA & PERSISTENCE LAYER", fill="#334155", font=font_layer)
    draw.rounded_rectangle([350, 580, 600, 640], radius=8, fill="#fef3c7", outline="#d97706", width=2)
    draw.text((370, 605), "MongoDB (PyMongo / JSON Store)", fill="#0f172a", font=font_comp)
    draw.rounded_rectangle([630, 580, 880, 640], radius=8, fill="#ffffff", outline="#0d9488", width=2)
    draw.text((680, 605), "Uploads Temp Storage", fill="#0f172a", font=font_comp)

    img.save(png_path)
    print(f"[Diagram] Generated PNG architecture diagram: {png_path}")

if __name__ == "__main__":
    generate_flow_diagram()
    generate_architecture_diagram()
