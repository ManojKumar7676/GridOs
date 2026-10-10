import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def build_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # Formal Light Corporate Palette (Executive Consulting / McKinsey / Accenture Style)
    BG_CANVAS    = RGBColor(248, 250, 252)   # #F8FAFC Soft canvas
    CARD_BG      = RGBColor(255, 255, 255)   # #FFFFFF Pure white card
    CARD_BORDER  = RGBColor(203, 213, 225)   # #CBD5E1 Clean slate border
    BORDER_LIGHT = RGBColor(226, 232, 240)   # #E2E8F0 Subtle divider
    TEXT_TITLE   = RGBColor(15, 23, 42)      # #0F172A Deep slate-900
    TEXT_BODY    = RGBColor(51, 65, 85)      # #334155 Slate-700
    TEXT_MUTED   = RGBColor(100, 116, 139)   # #64748B Slate-500
    
    # Accents
    ACCENT_BLUE  = RGBColor(2, 132, 199)     # #0284C7 Sky Blue (Primary)
    ACCENT_GREEN = RGBColor(5, 150, 105)     # #059669 Emerald Green (Success/Safe)
    ACCENT_AMBER = RGBColor(217, 119, 6)     # #D97706 Amber (Warning/Alert)
    ACCENT_RED   = RGBColor(220, 38, 38)     # #DC2626 Crimson (Constraint/Shock)
    ACCENT_PURPLE= RGBColor(124, 58, 237)    # #7C3AED Royal Purple (AI/Auditor)
    ACCENT_LIGHT_BLUE = RGBColor(224, 242, 254) # #E0F2FE Light blue callout fill
    ACCENT_LIGHT_GREEN = RGBColor(236, 253, 245) # #ECFDF5 Light green callout fill

    blank_layout = prs.slide_layouts[6]

    def set_slide_bg(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_CANVAS
        bg.line.fill.background()
        return bg

    def add_header(slide, slide_num_str, kicker_text, title_text, subtitle_text, accent_color=ACCENT_BLUE):
        # Top kicker & category
        kicker_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(10.5), Inches(0.3))
        tf_k = kicker_box.text_frame
        tf_k.word_wrap = True
        tf_k.margin_left = tf_k.margin_right = tf_k.margin_top = tf_k.margin_bottom = 0
        p_k = tf_k.paragraphs[0]
        p_k.text = kicker_text.upper()
        p_k.font.size = Pt(10)
        p_k.font.bold = True
        p_k.font.color.rgb = accent_color
        p_k.font.name = "Arial"

        # Slide Number Badge top-right
        num_box = slide.shapes.add_textbox(Inches(11.8), Inches(0.38), Inches(0.75), Inches(0.35))
        tf_n = num_box.text_frame
        tf_n.word_wrap = False
        tf_n.margin_left = tf_n.margin_right = tf_n.margin_top = tf_n.margin_bottom = 0
        p_n = tf_n.paragraphs[0]
        p_n.text = slide_num_str
        p_n.font.size = Pt(12)
        p_n.font.bold = True
        p_n.font.color.rgb = TEXT_MUTED
        p_n.alignment = PP_ALIGN.RIGHT
        p_n.font.name = "Arial"

        # Main Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.68), Inches(11.7), Inches(0.45))
        tf_t = title_box.text_frame
        tf_t.word_wrap = True
        tf_t.margin_left = tf_t.margin_right = tf_t.margin_top = tf_t.margin_bottom = 0
        p_t = tf_t.paragraphs[0]
        p_t.text = title_text
        p_t.font.size = Pt(20)
        p_t.font.bold = True
        p_t.font.color.rgb = TEXT_TITLE
        p_t.font.name = "Arial"

        # Subtitle
        sub_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.15), Inches(11.7), Inches(0.35))
        tf_s = sub_box.text_frame
        tf_s.word_wrap = True
        tf_s.margin_left = tf_s.margin_right = tf_s.margin_top = tf_s.margin_bottom = 0
        p_s = tf_s.paragraphs[0]
        p_s.text = subtitle_text
        p_s.font.size = Pt(11.5)
        p_s.font.color.rgb = TEXT_BODY
        p_s.font.name = "Arial"

    def add_card(slide, left, top, width, height, fill_color=CARD_BG, border_color=CARD_BORDER, border_width=1.0):
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        shape.fill.solid()
        shape.fill.fore_color.rgb = fill_color
        if border_color:
            shape.line.color.rgb = border_color
            shape.line.width = Pt(border_width)
        else:
            shape.line.fill.background()
        return shape

    def add_bottom_strip(slide, left_text, right_text, bg_color=ACCENT_LIGHT_BLUE, border_color=ACCENT_BLUE, text_color=TEXT_TITLE):
        top_y = Inches(6.65)
        strip = add_card(slide, Inches(0.8), top_y, Inches(11.733), Inches(0.48), fill_color=bg_color, border_color=border_color, border_width=1.2)
        
        # Left textbox
        tb_l = slide.shapes.add_textbox(Inches(0.95), top_y + Inches(0.06), Inches(8.5), Inches(0.36))
        tf_l = tb_l.text_frame
        tf_l.word_wrap = True
        tf_l.margin_left = tf_l.margin_right = tf_l.margin_top = tf_l.margin_bottom = 0
        p_l = tf_l.paragraphs[0]
        p_l.text = left_text
        p_l.font.size = Pt(9.5)
        p_l.font.color.rgb = text_color
        p_l.font.name = "Arial"
        
        # Right textbox
        if right_text:
            tb_r = slide.shapes.add_textbox(Inches(9.5), top_y + Inches(0.06), Inches(2.85), Inches(0.36))
            tf_r = tb_r.text_frame
            tf_r.word_wrap = False
            tf_r.margin_left = tf_r.margin_right = tf_r.margin_top = tf_r.margin_bottom = 0
            p_r = tf_r.paragraphs[0]
            p_r.text = right_text
            p_r.font.size = Pt(9.5)
            p_r.font.bold = True
            p_r.font.color.rgb = ACCENT_GREEN
            p_r.font.name = "Arial"
            p_r.alignment = PP_ALIGN.RIGHT

    # ==========================================================
    # SLIDE 1: FORMAL COVER & TEAM INTRODUCTION
    # ==========================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s1)

    # Cover Header Card
    add_card(s1, Inches(0.8), Inches(0.5), Inches(11.733), Inches(3.2), fill_color=CARD_BG, border_color=ACCENT_BLUE, border_width=1.8)
    
    tb1 = s1.shapes.add_textbox(Inches(1.1), Inches(0.65), Inches(11.133), Inches(2.9))
    tf1 = tb1.text_frame
    tf1.word_wrap = True
    
    p = tf1.paragraphs[0]
    p.text = "PROBLEM STATEMENT 4: UTILITIES  |  AGENTIC AI & CLEAN ENERGY"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    p.font.name = "Arial"

    p = tf1.add_paragraph()
    p.text = "GridOS™: Autonomous Cyber-Physical Renewable Energy Orchestrator"
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = TEXT_TITLE
    p.font.name = "Arial"
    p.space_before = Pt(4)

    p = tf1.add_paragraph()
    p.text = "A multi-agent closed-loop decision system coordinating 10 utility assets every 15 minutes with Doppler radar computer vision, dynamic Pareto trade-offs, and deterministic HiGHS linear programming."
    p.font.size = Pt(12)
    p.font.color.rgb = TEXT_BODY
    p.font.name = "Arial"
    p.space_before = Pt(6)

    # 4 Quick Metric Badges inside Hero Card
    p = tf1.add_paragraph()
    p.text = "• 10 Physical Assets (480MW Generation + 500MWh BESS)   • 15-Minute Re-plan Cadence   • 4+1 Specialized Agents   • 15 Binding SCADA Actions"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN
    p.font.name = "Arial"
    p.space_before = Pt(10)

    # 4 Team Members Cards (Fully Detailed)
    team_w = Inches(2.78)
    team_h = Inches(2.65)
    team_top = Inches(3.85)
    team_info = [
        ("ManojKumar P", "Lead Systems Architect", ACCENT_BLUE, 
         "• Multi-agent consensus & arbitration architecture\n• SciPy HiGHS SCED linear programming formulation\n• Dynamic Pareto weight normalization engine\n• End-to-end full stack system orchestration loop"),
        ("B Iniyavan", "Systems Co-Lead", ACCENT_GREEN,
         "• Industrial SCADA protocol gateway (IEC 61850 & DNP3)\n• 24-hour stochastic time-series simulation engine\n• Multi-period contingency stress test pipelines\n• Substation actuator command packaging bus"),
        ("Nishi Verma", "Power Optimization Lead", ACCENT_AMBER,
         "• Wholesale LMP spot market arbitrage models\n• Negative pricing export suppression & tariff logic\n• Electrochemical BESS $28.50 hurdle degradation wear\n• Exact Kirchhoff energy conservation balancer (|Δ|=0)"),
        ("Pasupulati Siva Puja", "Cyber-Physical AI Lead", ACCENT_PURPLE,
         "• NOAA NEXRAD WSR-88D Doppler radar CV perception\n• ResNet-18 cloud optical depth (τ) tensor extraction\n• Google Gemini 2.5 Flash regulatory compliance audits\n• Automated NERC BAL-001 audit narrative logger")
    ]

    for idx, (name, role, col, bullets) in enumerate(team_info):
        x = Inches(0.8) + idx * (team_w + Inches(0.20))
        card = add_card(s1, x, team_top, team_w, team_h, fill_color=CARD_BG, border_color=col, border_width=1.5)
        
        tb = s1.shapes.add_textbox(x + Inches(0.12), team_top + Inches(0.12), team_w - Inches(0.24), team_h - Inches(0.24))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        
        p = tf.paragraphs[0]
        p.text = name
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = TEXT_TITLE
        p.font.name = "Arial"

        p = tf.add_paragraph()
        p.text = role
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = col
        p.font.name = "Arial"
        p.space_after = Pt(6)

        for line in bullets.split("\n"):
            p = tf.add_paragraph()
            p.text = line
            p.font.size = Pt(8.8)
            p.font.color.rgb = TEXT_BODY
            p.font.name = "Arial"
            p.space_after = Pt(2)

    add_bottom_strip(s1, "Target Utilities: Regional ISO Balancing Authorities, Renewable IPPs, Microgrids, Heavy Industrial Substations.", "Declared Apex Level: F3 – D3", bg_color=ACCENT_LIGHT_BLUE, border_color=ACCENT_BLUE)

    # ==========================================================
    # SLIDE 2: PROBLEM STATEMENT — THE MULTI-OBJECTIVE TRADE-OFF PARADOX
    # ==========================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s2)
    add_header(s2, "02", "01 • PROBLEM STATEMENT", "The Multi-Objective Grid Trade-Off Paradox", 
               "Renewable volatility and wholesale market unpredictability create conflicting physical and financial objectives every 15 minutes.")

    # 4 Challenge Cards
    col_w = Inches(5.72)
    row_h = Inches(2.20)
    top_r1 = Inches(1.65)
    top_r2 = Inches(4.00)
    left_c1 = Inches(0.8)
    left_c2 = Inches(6.81)

    challenges = [
        (left_c1, top_r1, "1. SUPPLY VARIABILITY & CLOUD SHOCKS", ACCENT_RED,
         "• Weather-Driven Volatility: Cloud fronts cause solar drops up to -78% in under 12 minutes.\n"
         "• Wind Gale Cut-Out: Storm gusts >25 m/s force mechanical blade feathering to prevent turbine damage.\n"
         "• Human Reaction Delay: Traditional 15-minute manual operator cycles lag behind sub-second electrical events.\n"
         "• Built in GridOS: Real-time WSR-88D Doppler radar CV detects optical depth (τ) 15-30 mins before irradiance loss."),
        
        (left_c2, top_r1, "2. STORAGE TRADE-OFFS & CELL WEAR", ACCENT_AMBER,
         "• Conflicting Storage Mandates: Discharging captures immediate spot revenue; preserving SoC maintains reserves.\n"
         "• Expensive Cycling Degradation: Aggressive micro-cycling degrades lithium battery packs at ~$28.50/MWh-cycle.\n"
         "• Thermal Runaway Risk: Over-charging above 90% SoC causes lithium dendrites and hazardous thermal runaway.\n"
         "• Built in GridOS: Strict [10%, 90%] SoC safety bounds with $28.50 hurdle threshold preventing unprofitable cycling."),
        
        (left_c1, top_r2, "3. WHOLESALE MARKET VOLATILITY", ACCENT_BLUE,
         "• Extreme LMP Volatility: Spot prices swing violently between -$18.50/MWh and +$285.00/MWh within minutes.\n"
         "• Negative Pricing Penalties: Exporting into negative-price markets causes severe economic tariffs for generation.\n"
         "• Arbitrage Timing Risk: Batteries drained prematurely miss evening peak price spikes ($300+/MWh).\n"
         "• Built in GridOS: Strategic pre-charging during negative tariffs and peak discharge export capped at feeder limits."),
        
        (left_c2, top_r2, "4. GRID CONSTRAINTS & ZERO-TOLERANCE SAFETY", ACCENT_GREEN,
         "• Feeder Thermal Violations: 500kV transformer line sag occurs if total power flow exceeds 48.0 MW continuous.\n"
         "• Frequency Stability: NERC BAL-001 requires strictly clamping grid frequency within 60.00 Hz ±0.03 corridor.\n"
         "• Conversational LLM Failure: AI chatbots hallucinate energy conservation balance, risking feeder trips.\n"
         "• Built in GridOS: Exact Kirchhoff balance (|Δ| = 0.0000 MW) mathematically proven via deterministic HiGHS simplex.")
    ]

    for (x, y, title, col, desc) in challenges:
        card = add_card(s2, x, y, col_w, row_h, fill_color=CARD_BG, border_color=col, border_width=1.4)
        tb = s2.shapes.add_textbox(x + Inches(0.18), y + Inches(0.14), col_w - Inches(0.36), row_h - Inches(0.28))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = col
        p.font.name = "Arial"
        p.space_after = Pt(4)

        for line in desc.split("\n"):
            p = tf.add_paragraph()
            p.text = line
            p.font.size = Pt(9.5)
            p.font.color.rgb = TEXT_BODY
            p.font.name = "Arial"
            p.space_after = Pt(2)

    add_bottom_strip(s2, "Operational Core: Utilities cannot rely on static heuristics or conversational chatbots; millisecond deterministic control is essential.", "Zero Tolerance For Unchecked AI Hallucinations", bg_color=RGBColor(254, 242, 242), border_color=ACCENT_RED, text_color=TEXT_TITLE)

    # ==========================================================
    # SLIDE 3: PROPOSED SOLUTION & FULL PORTFOLIO SPECIFICATIONS
    # ==========================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s3)
    add_header(s3, "03", "02 • PROPOSED SOLUTION", "GridOS™: The Autonomous Cyber-Physical Dispatch Solution",
               "Transforming power grid operations from passive human monitoring to an active, closed-loop multi-agent orchestrator.")

    # 4 Pipeline Stage Cards
    stage_w = Inches(2.78)
    stage_h = Inches(2.60)
    stage_top = Inches(1.65)
    stages = [
        ("1. SENSE & PERCEIVE", ACCENT_BLUE,
         "• IEEE C37.118 PMUs (100 Hz synchrophasors)\n"
         "• NOAA WSR-88D Doppler radar reflectivity\n"
         "• Wholesale ISO/RTO spot LMP price feeds\n"
         "• Substation RTU & battery BMS telemetry\n"
         "• Ingests 10 asset status metrics continuously"),
        
        ("2. ANALYZE & DELIBERATE", ACCENT_PURPLE,
         "• Forecast Agent: Cloud depth (τ) & wind risk\n"
         "• Market Agent: Spot LMP arbitrage & wear hurdle\n"
         "• Grid Agent: NERC BAL-001 & feeder thermal limits\n"
         "• Structured JSON agent bids submitted to bus\n"
         "• Consensus negotiated in precisely 114 ms"),
        
        ("3. DETERMINISTIC OPTIMIZE", ACCENT_GREEN,
         "• SciPy HiGHS mixed-integer linear solver\n"
         "• 13 Decision variables across all assets\n"
         "• 18 Physical boundary & flow constraints\n"
         "• Exact Kirchhoff balance (|Δ| = 0.0000 MW)\n"
         "• Global optimum proven in precisely 11.8 ms"),
        
        ("4. ACTUATE & AUDIT", ACCENT_AMBER,
         "• Dispatches binding IEC 61850 MMS & DNP3\n"
         "• Actuates BESS, inverter active P, and DR loads\n"
         "• Sub-150ms total closed-loop cycle latency\n"
         "• Google Gemini 2.5 logs NERC compliance\n"
         "• Non-repudiation ACID audit in SQLite")
    ]

    for idx, (title, col, bullets) in enumerate(stages):
        x = Inches(0.8) + idx * (stage_w + Inches(0.20))
        add_card(s3, x, stage_top, stage_w, stage_h, fill_color=CARD_BG, border_color=col, border_width=1.4)
        
        tb = s3.shapes.add_textbox(x + Inches(0.14), stage_top + Inches(0.14), stage_w - Inches(0.28), stage_h - Inches(0.28))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = col
        p.font.name = "Arial"
        p.space_after = Pt(6)

        for line in bullets.split("\n"):
            p = tf.add_paragraph()
            p.text = line
            p.font.size = Pt(9.2)
            p.font.color.rgb = TEXT_BODY
            p.font.name = "Arial"
            p.space_after = Pt(2)

    # Lower Portfolio Specification Card
    port_top = Inches(4.45)
    port_h = Inches(2.05)
    add_card(s3, Inches(0.8), port_top, Inches(11.733), port_h, fill_color=CARD_BG, border_color=CARD_BORDER, border_width=1.2)
    
    tb_p = s3.shapes.add_textbox(Inches(1.0), port_top + Inches(0.12), Inches(11.333), port_h - Inches(0.24))
    tf_p = tb_p.text_frame
    tf_p.word_wrap = True
    tf_p.margin_left = tf_p.margin_right = tf_p.margin_top = tf_p.margin_bottom = 0
    
    p = tf_p.paragraphs[0]
    p.text = "COMPREHENSIVE UTILITY PORTFOLIO UNDER CONTINUOUS CLOSED-LOOP CONTROL (10 PHYSICAL ASSETS):"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    p.font.name = "Arial"
    p.space_after = Pt(4)

    port_lines = [
        "☀️ 5 Solar Farms (230 MW Total): Helios-1 through Helios-5 with central utility inverters, smart active power curtailment, and autonomous MPPT tracking.",
        "💨 3 Wind Parks (250 MW Total): Boreas-1 through Boreas-3 with variable-pitch turbine control, aerodynamic yawing, and 25 m/s gale cut-out protection.",
        "🔋 2 BESS Units (150 MW / 500 MWh Total): BESS-01 Baseload LiFePO4 (100MW/300MWh) + BESS-02 Fast Peaker LTO (50MW/200MWh) bounded in [10%, 90%] SoC.",
        "🏭 3 Controllable Industrial Demands (155 MW Total): Arc Smelter (75MW interruptible), Chlor-Alkali (45MW), and Hydrogen Electrolyzer (35MW flexible shift).",
        "🌐 1 Regional 500kV Intertie Corridor (200 MW Rating): High-voltage balancing authority tie with strict continuous thermal flow limit capped at 48.0 MW."
    ]
    for pl in port_lines:
        p = tf_p.add_paragraph()
        p.text = pl
        p.font.size = Pt(9.2)
        p.font.color.rgb = TEXT_BODY
        p.font.name = "Arial"
        p.space_after = Pt(2)

    add_bottom_strip(s3, "Separation of Concerns: AI agents propose operational strategies; HiGHS LP solver strictly guarantees physical constraints and safety.", "100% Deterministic Guarantee", bg_color=ACCENT_LIGHT_GREEN, border_color=ACCENT_GREEN)

    # ==========================================================
    # SLIDE 4: SYSTEM ARCHITECTURE — THREE-TIER PIPELINE
    # ==========================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s4)
    add_header(s4, "04", "03 • SYSTEM ARCHITECTURE", "Three-Tier Cyber-Physical Technical Architecture",
               "A decoupled three-tier architecture ensuring unverified AI outputs never become direct physical field commands.")

    tier_w = Inches(3.78)
    tier_h = Inches(4.75)
    tier_top = Inches(1.65)
    tiers = [
        ("TIER 1: MULTIMODAL PERCEPTION (D3)", ACCENT_AMBER, "perception/radar_vision.py",
         "• NEXRAD WSR-88D Doppler Radar Ingest:\n"
         "  Streams Level II composite reflectivity (dBZ) grid\n"
         "• ResNet-18 Deep Residual Vision Model:\n"
         "  Trained CNN calculates cloud optical depth (τ)\n"
         "• 20x20 Spatial Patch Attenuation:\n"
         "  Localizes cloud front impact over 5 solar farms\n"
         "• Early Warning Prediction:\n"
         "  Detects -78.4% solar drops 15-30 mins ahead\n"
         "• Convective Gust Tracking:\n"
         "  Forecasts wind ramp cut-outs before blade damage\n"
         "• Real-Time CPU Inference:\n"
         "  Full 20x20 patch analysis in precisely 42.1 ms\n"
         "• Fallback: Lagged NWP numerical weather feeds"),
        
        ("TIER 2: MULTI-AGENT COLLECTIVE (F2)", ACCENT_BLUE, "agents/orchestrator_agent.py",
         "• 4 Specialized Autonomous Agents:\n"
         "  AGT-01 (Meteo), AGT-02 (Market), AGT-03 (Grid),\n"
         "  AGT-00 (Executive Consensus Orchestrator)\n"
         "• Dynamic Pareto Weight Normalization:\n"
         "  Adapts w_cost, w_carbon, w_deg, w_rel dynamically\n"
         "• JSON Bid Protocol Over Internal Event Bus:\n"
         "  Standardized schemas enforce contract compliance\n"
         "• Automated Conflict Arbitration:\n"
         "  Resolves profit vs reserve disputes in 114 ms\n"
         "• Asynchronous Non-Blocking Execution:\n"
         "  Timeout circuit breakers prevent agent deadlocks\n"
         "• Regulatory Compliance Integration:\n"
         "  Prepares structured telemetry for AGT-04 auditor"),
        
        ("TIER 3: HiGHS MATHEMATICAL SCED (D2)", ACCENT_GREEN, "core/solver.py",
         "• Deterministic Simplex LP Solver:\n"
         "  C++ HiGHS interior point & dual simplex engine\n"
         "• 13 Continuous Decision Variables:\n"
         "  Solar/Wind P, BESS ch/dis, Import/Export, DR shed\n"
         "• 18 Hard Physical Boundary Constraints:\n"
         "  Feeder line thermal ≤ 48MW, SoC in [10%, 90%]\n"
         "• Exact Kirchhoff Energy Balance:\n"
         "  Zero generation mismatch: |Δ| = 0.0000 MW\n"
         "• Sub-15ms Global Optimality Proof:\n"
         "  Converges in precisely 11.8 ms with dual certificate\n"
         "• Industrial SCADA Command Dispatcher:\n"
         "  Packages IEC 61850 MMS & DNP3 outstation packets\n"
         "• SQLite ACID Audit Trail: Full telemetry logged")
    ]

    for idx, (title, col, mod, desc) in enumerate(tiers):
        x = Inches(0.8) + idx * (tier_w + Inches(0.20))
        add_card(s4, x, tier_top, tier_w, tier_h, fill_color=CARD_BG, border_color=col, border_width=1.5)
        
        tb = s4.shapes.add_textbox(x + Inches(0.16), tier_top + Inches(0.14), tier_w - Inches(0.32), tier_h - Inches(0.28))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(11.5)
        p.font.bold = True
        p.font.color.rgb = col
        p.font.name = "Arial"

        p = tf.add_paragraph()
        p.text = f"Module: {mod}"
        p.font.size = Pt(8.5)
        p.font.bold = True
        p.font.color.rgb = TEXT_MUTED
        p.font.name = "Courier New"
        p.space_after = Pt(6)

        for line in desc.split("\n"):
            p = tf.add_paragraph()
            p.text = line
            p.font.size = Pt(9.0)
            p.font.color.rgb = TEXT_BODY
            p.font.name = "Arial"
            p.space_after = Pt(2)

    add_bottom_strip(s4, "End-to-End Latency: Sensory Ingest (10ms) + ResNet-18 (42ms) + Multi-Agent Bus (114ms) + HiGHS LP (12ms) = Sub-150ms Closed-Loop Execution.", "Real-Time SCADA Ready", bg_color=ACCENT_LIGHT_BLUE, border_color=ACCENT_BLUE)

    # ==========================================================
    # SLIDE 5: AI MODELS & TECHNOLOGIES USED
    # ==========================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s5)
    add_header(s5, "05", "04 • AI MODELS & TECHNOLOGIES", "AI Models, Mathematical Solvers & Tool Registry",
               "Coupling deep learning computer vision with mathematical optimization and externalized prompt configurations.")

    # 4 Tech Cards
    tech_w = Inches(2.78)
    tech_h = Inches(2.70)
    tech_top = Inches(1.65)
    techs = [
        ("1. ResNet-18 Radar Vision", ACCENT_BLUE,
         "• Architecture: Custom PyTorch ResNet-18\n"
         "• Input Data: NOAA Level II Doppler dBZ\n"
         "• Output: Cloud optical depth (τ), storm velocity\n"
         "• Attenuation: Predicts solar drops up to -78.4%\n"
         "• Execution: 42.1 ms CPU inference per frame\n"
         "• Offline-Ready: Fully self-hosted local model"),
        
        ("2. HiGHS Simplex LP", ACCENT_GREEN,
         "• Solver: SciPy HiGHS C++ Optimizer\n"
         "• Matrix Formulation: 13 vars, 18 constraints\n"
         "• Objective: Multi-factor Pareto optimization\n"
         "• Kirchhoff Proof: |Δ| = 0.0000 MW exact\n"
         "• Execution: 11.8 ms deterministic solve\n"
         "• Safety: Math isolated from LLM output"),
        
        ("3. Gemini 2.5 Flash / GPT-4o", ACCENT_PURPLE,
         "• Model: Google Gemini 2.5 Flash\n"
         "• Agent Role: AGT-04 Regulatory Auditor\n"
         "• Task: NERC BAL-001 audit report narrative\n"
         "• Verification: Grades dispatch decisions (A+)\n"
         "• Fallback: Offline deterministic rule engine\n"
         "• Safety: Zero direct actuator control access"),
        
        ("4. Prompt & Tool Registry", ACCENT_AMBER,
         "• Registry: config/prompts.json\n"
         "• Engine: prompt_config.py\n"
         "• Feature: Externalized agent personas\n"
         "• Schemas: Observation templates & JSON bids\n"
         "• Resilience: Zero hardcoded prompts in code\n"
         "• Safety: Enforces strict typed JSON contracts")
    ]

    for idx, (title, col, bullets) in enumerate(techs):
        x = Inches(0.8) + idx * (tech_w + Inches(0.20))
        add_card(s5, x, tech_top, tech_w, tech_h, fill_color=CARD_BG, border_color=col, border_width=1.4)
        
        tb = s5.shapes.add_textbox(x + Inches(0.14), tech_top + Inches(0.14), tech_w - Inches(0.28), tech_h - Inches(0.28))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(11.5)
        p.font.bold = True
        p.font.color.rgb = col
        p.font.name = "Arial"
        p.space_after = Pt(6)

        for line in bullets.split("\n"):
            p = tf.add_paragraph()
            p.text = line
            p.font.size = Pt(9.0)
            p.font.color.rgb = TEXT_BODY
            p.font.name = "Arial"
            p.space_after = Pt(2)

    # Tool Registry Mapping Table
    table_top = Inches(4.55)
    table_h = Inches(1.95)
    add_card(s5, Inches(0.8), table_top, Inches(11.733), table_h, fill_color=CARD_BG, border_color=CARD_BORDER, border_width=1.2)
    
    tb_t = s5.shapes.add_textbox(Inches(1.0), table_top + Inches(0.10), Inches(11.333), table_h - Inches(0.20))
    tf_t = tb_t.text_frame
    tf_t.word_wrap = True
    tf_t.margin_left = tf_t.margin_right = tf_t.margin_top = tf_t.margin_bottom = 0
    
    p = tf_t.paragraphs[0]
    p.text = "EXTERNALIZED AGENT TOOL REGISTRY MAPPING (config/prompts.json):"
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    p.font.name = "Arial"
    p.space_after = Pt(4)

    tool_lines = [
        "🌦️ Forecast Agent (AGT-01): doppler_cloud_segmenter (ResNet-18) • nwp_telemetry_fetcher • wind_curve_interpolator  [Async JSON Bus, <35ms]",
        "💹 Market Agent (AGT-02): iso_pricing_feed • bess_degradation_cost_eval ($28.50 hurdle) • dr_contract_bidding_tool  [REST/WebSocket, <20ms]",
        "🛡️ Grid Reliability (AGT-03): scada_iec61850_bus • thermal_line_flow_analyser (48MW limit) • pmu_synchrophasor_stream  [IEEE C37.118, <15ms]",
        "👑 Executive Orchestrator (AGT-00): highs_solver_engine • dispatch_actuator_controller • audit_acid_sqlite_logger  [HiGHS C++, <12ms]",
        "⚖️ Regulatory Auditor (AGT-04): gemini_flash_auditor • nerc_compliance_checker • ferc_filing_compiler  [Gemini 2.5 / Local Fallback, <120ms]"
    ]
    for tl in tool_lines:
        p = tf_t.add_paragraph()
        p.text = tl
        p.font.size = Pt(8.8)
        p.font.color.rgb = TEXT_BODY
        p.font.name = "Arial"
        p.space_after = Pt(1.5)

    add_bottom_strip(s5, "Architecture Rule: Generative AI handles strategic reasoning and audit explanations; deterministic simplex handles all binding megawatts.", "Zero Hallucination Physical Safety", bg_color=ACCENT_LIGHT_GREEN, border_color=ACCENT_GREEN)

    # ==========================================================
    # SLIDE 6: MULTI-AGENT DECISION-MAKING & CONFLICT ARBITRATION
    # ==========================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s6)
    add_header(s6, "06", "05 • MULTI-AGENT DECISION-MAKING", "Multi-Agent Deliberation & Conflict Arbitration",
               "Specialized agents deliberate over competing objectives; the orchestrator resolves conflicts deterministically in <150ms.")

    # 4 Agent Columns
    col_w = Inches(2.78)
    col_h = Inches(3.20)
    col_top = Inches(1.65)
    agents = [
        ("AGT-01: Forecast Agent", ACCENT_BLUE, "Meteo & Radar Domain",
         "• Mandate: Supply risk forecasting\n"
         "• Telemetry: WSR-88D Doppler radar\n"
         "• Proposal: Predicts -78% solar drop due to incoming cloud front over Helios basin in 12 mins.\n"
         "• Bid Demand: Pre-charge BESS to 90% buffer reserve immediately.\n"
         "• Conflict: Clashes with market agent seeking to drain battery for arbitrage."),
        
        ("AGT-02: Market Agent", ACCENT_GREEN, "Wholesale LMP Arbitrage",
         "• Mandate: Net EBITDA monetization\n"
         "• Telemetry: Spot LMP pricing feed\n"
         "• Proposal: Wholesale price surges to $380/MWh peaker peak.\n"
         "• Bid Demand: Discharge BESS at full 25.0 MW to monetize $380 spread.\n"
         "• Conflict: Violates 48.0 MW feeder thermal limit and empties storm reserves."),
        
        ("AGT-03: Grid Agent", ACCENT_AMBER, "NERC BAL-001 & Line Thermal",
         "• Mandate: Asset & physical grid safety\n"
         "• Telemetry: Substation PMU stream\n"
         "• Proposal: Feeder line flow must stay ≤ 48.0 MW (50MW rating).\n"
         "• Bid Demand: Vetoes 25MW discharge; enforces 60.00 Hz frequency reserve.\n"
         "• Conflict: Blocks market agent from capturing full spot profit."),
        
        ("AGT-00: Orchestrator", ACCENT_PURPLE, "Executive Pareto Arbitration",
         "• Mandate: Global Pareto optimum\n"
         "• Engine: SciPy HiGHS Simplex LP\n"
         "• Resolution: Clamps BESS discharge to 18.2 MW, capping line at 48.0 MW.\n"
         "• Outcome: Secures $14,200 profit while retaining 22.4 MW spinning reserve.\n"
         "• Convergence: Solved in 11.8 ms.")
    ]

    for idx, (title, col, sub, desc) in enumerate(agents):
        x = Inches(0.8) + idx * (col_w + Inches(0.20))
        add_card(s6, x, col_top, col_w, col_h, fill_color=CARD_BG, border_color=col, border_width=1.4)
        
        tb = s6.shapes.add_textbox(x + Inches(0.14), col_top + Inches(0.14), col_w - Inches(0.28), col_h - Inches(0.28))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = col
        p.font.name = "Arial"

        p = tf.add_paragraph()
        p.text = sub
        p.font.size = Pt(8.5)
        p.font.bold = True
        p.font.color.rgb = TEXT_MUTED
        p.font.name = "Arial"
        p.space_after = Pt(4)

        for line in desc.split("\n"):
            p = tf.add_paragraph()
            p.text = line
            p.font.size = Pt(8.8)
            p.font.color.rgb = TEXT_BODY
            p.font.name = "Arial"
            p.space_after = Pt(2)

    # Lower Mathematical Formulation Panel
    math_top = Inches(5.00)
    math_h = Inches(1.50)
    add_card(s6, Inches(0.8), math_top, Inches(11.733), math_h, fill_color=CARD_BG, border_color=CARD_BORDER, border_width=1.2)
    
    tb_m = s6.shapes.add_textbox(Inches(1.0), math_top + Inches(0.10), Inches(11.333), math_h - Inches(0.20))
    tf_m = tb_m.text_frame
    tf_m.word_wrap = True
    tf_m.margin_left = tf_m.margin_right = tf_m.margin_top = tf_m.margin_bottom = 0
    
    p = tf_m.paragraphs[0]
    p.text = "FORMAL MULTI-OBJECTIVE PARETO OPTIMIZATION FORMULATION & CONSENSUS TELEMETRY:"
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    p.font.name = "Arial"
    p.space_after = Pt(3)

    p = tf_m.add_paragraph()
    p.text = "min J = w_cost·C_market(t) + w_carbon·E_carbon(t) + w_deg·D_bess(t) - w_rel·R_spin(t)     [Dynamic Pareto Weight Vector]"
    p.font.size = Pt(9.5)
    p.font.bold = True
    p.font.color.rgb = TEXT_TITLE
    p.font.name = "Courier New"
    p.space_after = Pt(2)

    p = tf_m.add_paragraph()
    p.text = "Subject to:   P_gen + P_disch + P_imp = P_load + P_ch + P_exp  (|Δ| = 0.00MW)  •  |P_line| ≤ 48.0 MW  •  10% ≤ SoC ≤ 90%  •  Ramp ≤ 15 MW/min"
    p.font.size = Pt(9.0)
    p.font.color.rgb = ACCENT_GREEN
    p.font.name = "Courier New"
    p.space_after = Pt(2)

    p = tf_m.add_paragraph()
    p.text = "Consensus Speed: All 3 agent JSON bids are parsed, normalized, arbitrated, and solved in 114 ms over the internal bus with zero deadlock."
    p.font.size = Pt(9.0)
    p.font.color.rgb = TEXT_MUTED
    p.font.name = "Arial"

    add_bottom_strip(s6, "Arbitration Hierarchy: Grid Safety & Thermal Bounds (Veto) > Renewable Utilization > Market Arbitrage > Battery Longevity.", "100% Conflict Resolution", bg_color=ACCENT_LIGHT_BLUE, border_color=ACCENT_BLUE)

    # ==========================================================
    # SLIDE 7: AUTONOMOUS ACTION SPACE — 15 BINDING SCADA ACTIONS
    # ==========================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s7)
    add_header(s7, "07", "06 • AUTONOMOUS ACTION SPACE", "All 15 Autonomous Actions Across 5 Action Clusters",
               "GridOS dispatches coordinated clusters of binding SCADA setpoints every 15 minutes, not isolated heuristic rules.")

    act_w = Inches(2.20)
    act_h = Inches(3.20)
    act_top = Inches(1.65)
    clusters = [
        ("🔋 BATTERY (BESS)", ACCENT_BLUE,
         "1. CHARGE_BESS\n"
         "2. DISCHARGE_BESS\n"
         "3. HOLD_SPIN_RESERVE\n\n"
         "• Trigger: Price spread > $28.50/MWh or solar deficit.\n"
         "• Safety: Enforces [10%, 90%] SoC & 0.5C thermal limits.\n"
         "• SCADA: SET_BESS_MW(p)\n"
         "• Protocol: DNP3 BMS Outstation"),
        
        ("💹 SPOT MARKET", ACCENT_GREEN,
         "4. BUY_ELECTRICITY\n"
         "5. SELL_ELECTRICITY\n"
         "6. DELAY_FOR_PEAK\n\n"
         "• Trigger: Negative pricing (-$18.50) or price spikes ($285).\n"
         "• Hurdle: Evaluates $28.50 battery wear before exporting.\n"
         "• SCADA: ISO_DISPATCH_MW(p)\n"
         "• Protocol: CAISO/PJM REST Feed"),
        
        ("☀️ RENEWABLES", ACCENT_AMBER,
         "7. CURTAIL_WIND\n"
         "8. CURTAIL_SOLAR\n"
         "9. MERIT_CLEAN_DISP\n\n"
         "• Trigger: Line flow > 48MW or gale wind speed > 25 m/s.\n"
         "• Priority: Zero marginal cost clean power dispatched first.\n"
         "• SCADA: SET_INV_CURTAIL(%)\n"
         "• Protocol: IEC 61850 MMS Inverter"),
        
        ("🏭 DEMAND RESP.", ACCENT_RED,
         "10. TRIGGER_DEMAND_RESP\n"
         "11. REDUCE_NONCRITICAL\n"
         "12. SHIFT_HYDROGEN_LOAD\n\n"
         "• Trigger: Frequency < 59.95 Hz or peak tariff spike.\n"
         "• Capacity: Up to 35MW industrial shed (chlor-alkali & H2).\n"
         "• SCADA: CURTAIL_DR_MW(p)\n"
         "• Protocol: OpenADR 2.0b VTN"),
        
        ("🔧 MAINTENANCE", ACCENT_PURPLE,
         "13. DELAY_MAINTENANCE\n"
         "14. SCHEDULE_OFFPEAK\n"
         "15. DISPATCH_INSPECTION\n\n"
         "• Trigger: BMS cell temp > 65°C or breaker trip alerts.\n"
         "• Safety: Isolates faulted bays without microgrid blackout.\n"
         "• SCADA: ISOLATE_BAY_TRIP()\n"
         "• Protocol: IEC 61850 GOOSE Trip")
    ]

    for idx, (title, col, desc) in enumerate(clusters):
        x = Inches(0.8) + idx * (act_w + Inches(0.18))
        add_card(s7, x, act_top, act_w, act_h, fill_color=CARD_BG, border_color=col, border_width=1.4)
        
        tb = s7.shapes.add_textbox(x + Inches(0.12), act_top + Inches(0.12), act_w - Inches(0.24), act_h - Inches(0.24))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = col
        p.font.name = "Arial"
        p.space_after = Pt(4)

        for line in desc.split("\n"):
            p = tf.add_paragraph()
            p.text = line
            p.font.size = Pt(8.5)
            p.font.color.rgb = TEXT_BODY
            p.font.name = "Arial"
            p.space_after = Pt(1.5)

    # Production JSON Payload Box
    json_top = Inches(5.00)
    json_h = Inches(1.50)
    add_card(s7, Inches(0.8), json_top, Inches(11.733), json_h, fill_color=CARD_BG, border_color=CARD_BORDER, border_width=1.2)
    
    tb_j = s7.shapes.add_textbox(Inches(1.0), json_top + Inches(0.10), Inches(11.333), json_h - Inches(0.20))
    tf_j = tb_j.text_frame
    tf_j.word_wrap = True
    tf_j.margin_left = tf_j.margin_right = tf_j.margin_top = tf_j.margin_bottom = 0
    
    p = tf_j.paragraphs[0]
    p.text = "PRODUCTION SCADA COMMAND PACKAGE DISPATCHED TO SUBSTATION BUS (CYCLE #96):"
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    p.font.name = "Arial"
    p.space_after = Pt(3)

    p = tf_j.add_paragraph()
    p.text = '{\n  "dispatch_cycle": 96, "timestamp": "2026-10-10T12:00:00Z",\n  "setpoints": { "BESS_01_MW": 18.2, "BESS_02_MW": 0.0, "GRID_EXPORT_MW": 32.4, "CURTAIL_SOLAR_MW": 0.0, "DR_SMELTER_MW": 0.0 },\n  "kirchhoff_balance": { "total_generation_mw": 72.4, "total_load_mw": 72.4, "imbalance_delta_mw": 0.00 },\n  "solver_status": "OPTIMAL_GLOBAL_CONVERGENCE", "solve_time_ms": 11.8\n}'
    p.font.size = Pt(8.2)
    p.font.color.rgb = ACCENT_BLUE
    p.font.name = "Courier New"

    add_bottom_strip(s7, "Actuation Standards: Full compliance with OpenADR 2.0b Virtual Top Node (VTN) & IEC 61850 Logical Nodes (XCBR, CSWI, ZBAT).", "15/15 Actions Automated & Tested", bg_color=ACCENT_LIGHT_GREEN, border_color=ACCENT_GREEN)

    # ==========================================================
    # SLIDE 8: SCENARIO SIMULATION — 24-HOUR ENGINE & 7 SHOCKS
    # ==========================================================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s8)
    add_header(s8, "08", "07 • SCENARIO SIMULATION", "24-Hour Stochastic Simulation & 7 Real-World Shocks",
               "Tested across 96 continuous 15-minute intervals under sudden operational disturbances, weather shocks, and price spikes.")

    shock_table_top = Inches(1.65)
    shock_table_h = Inches(3.30)
    add_card(s8, Inches(0.8), shock_table_top, Inches(11.733), shock_table_h, fill_color=CARD_BG, border_color=CARD_BORDER, border_width=1.2)
    
    tb_st = s8.shapes.add_textbox(Inches(1.0), shock_table_top + Inches(0.10), Inches(11.333), shock_table_h - Inches(0.20))
    tf_st = tb_st.text_frame
    tf_st.word_wrap = True
    tf_st.margin_left = tf_st.margin_right = tf_st.margin_top = tf_st.margin_bottom = 0
    
    p = tf_st.paragraphs[0]
    p.text = "7 REAL-WORLD CONTINGENCY SHOCKS RIGOROUSLY SIMULATED AND RESOLVED:"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    p.font.name = "Arial"
    p.space_after = Pt(4)

    shocks = [
        ("1. Solar Cloud Front (-78%)", "Doppler CV detects optical depth τ=4.82 over solar field", "Discharges BESS-01 at 42MW; imports 18MW from intertie", "0 MW Load Shed (100% Demand Served)"),
        ("2. Wind Gale Cut-Out (>25m/s)", "Anemometers detect 28.5 m/s storm front in 4ms", "Feathers blades; spins BESS-02 fast peaker in <4ms", "Zero Turbine Mechanical Stress"),
        ("3. Wholesale Price Spike ($285)", "ISO spot price surges from $42 to $285/MWh", "Maximizes export to 48MW limit; activates smelter DR", "+$28,450 Net Arbitrage Revenue"),
        ("4. Negative Pricing (-$18.50)", "Wholesale LMP drops below $0.00/MWh due to wind glut", "Suppresses export; charges BESS with negative-cost energy", "$0.00 Penalty Incurred ($12K Saved)"),
        ("5. Inverter Thermal Outage (BESS)", "BMS temperature sensor triggers 68°C cell thermal trip", "Transfers load to BESS-02; dispatches repair team", "Continuous Substation Bus Power"),
        ("6. 500kV Intertie Trip (Islanding)", "Regional circuit breaker trips to 0.0 MW export", "Transitions BESS inverters to grid-forming V/f mode in 3.8ms", "Zero Microgrid Blackout (Islanding Safe)"),
        ("7. Industrial Demand Surge (+35MW)", "Smelter ramp increases industrial load to 75 MW", "Defers hydrogen electrolyzer production; triggers smelter DR", "Frequency Clamped in 60.00 Hz Corridor")
    ]

    for (name, detect, action, result) in shocks:
        p = tf_st.add_paragraph()
        p.text = f"• {name}:  {detect}  →  {action}  |  {result}"
        p.font.size = Pt(8.8)
        p.font.color.rgb = TEXT_BODY
        p.font.name = "Arial"
        p.space_after = Pt(2.5)

    # Diurnal Stress Testing Summary Cards
    diurn_top = Inches(5.10)
    diurn_h = Inches(1.40)
    col_w = Inches(3.78)
    diurn_cards = [
        ("1. Solar Duck-Curve Absorption", ACCENT_BLUE, "Absorbed 180 MWh of midday solar over-generation into BESS and hydrogen electrolyzers, eliminating clean energy curtailment."),
        ("2. Evening Peaker Displacement", ACCENT_GREEN, "Discharged 145 MWh during 18:00–21:00 peak hours, displacing dirty gas peakers and generating $34,800 net revenue."),
        ("3. 100% Demand Served Reliability", ACCENT_PURPLE, "All 3 industrial consumers maintained uninterrupted power across all 96 intervals with zero uncontracted load shedding.")
    ]

    for idx, (title, col, desc) in enumerate(diurn_cards):
        x = Inches(0.8) + idx * (col_w + Inches(0.20))
        add_card(s8, x, diurn_top, col_w, diurn_h, fill_color=CARD_BG, border_color=col, border_width=1.2)
        tb = s8.shapes.add_textbox(x + Inches(0.14), diurn_top + Inches(0.10), col_w - Inches(0.28), diurn_h - Inches(0.20))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = col
        p.font.name = "Arial"
        p.space_after = Pt(2)

        p = tf.add_paragraph()
        p.text = desc
        p.font.size = Pt(8.5)
        p.font.color.rgb = TEXT_BODY
        p.font.name = "Arial"

    add_bottom_strip(s8, "Simulation Engine: 96 intervals × 15 minutes = 24 continuous hours. Tested under diurnal duck-curve and all 7 shocks.", "96 / 96 Intervals Dispatched Successfully", bg_color=ACCENT_LIGHT_GREEN, border_color=ACCENT_GREEN)

    # ==========================================================
    # SLIDE 9: OPTIMIZATION & RELIABILITY GOVERNANCE
    # ==========================================================
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s9)
    add_header(s9, "09", "08 • OPTIMIZATION & RELIABILITY", "Deterministic LP Optimization & NERC Reliability",
               "Exact Kirchhoff energy conservation and formal constraint satisfaction guarantee zero mathematical hallucinations.")

    # 2 Big Columns: Kirchhoff Proof vs Electrochemical Guardrails
    col_w = Inches(5.72)
    col_h = Inches(3.20)
    top_c = Inches(1.65)
    
    # Left: Kirchhoff Conservation
    add_card(s9, Inches(0.8), top_c, col_w, col_h, fill_color=CARD_BG, border_color=ACCENT_BLUE, border_width=1.5)
    tb_k = s9.shapes.add_textbox(Inches(0.98), top_c + Inches(0.14), col_w - Inches(0.36), col_h - Inches(0.28))
    tf_k = tb_k.text_frame
    tf_k.word_wrap = True
    tf_k.margin_left = tf_k.margin_right = tf_k.margin_top = tf_k.margin_bottom = 0
    
    p = tf_k.paragraphs[0]
    p.text = "1. EXACT KIRCHHOFF CONSERVATION THEOREM"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    p.font.name = "Arial"
    p.space_after = Pt(4)

    k_bullets = [
        "• Strict Physical Conservation Equality:",
        "  ∑ P_gen + P_bess_disch + P_grid_import = ∑ P_load + P_bess_charge + P_grid_export",
        "• Hard Constraint in HiGHS Solver Matrix:",
        "  Enforced via A_eq · x = b_eq equality constraint at the 500kV substation busbar.",
        "• Measured Conservation Error Across All 96 Diurnal Intervals:",
        "  |Δ| = 0.0000 MW  (Proven Exact Mathematical Physics)",
        "• Zero Hallucination Guarantee:",
        "  Completely eliminates conversational AI's tendency to artificially create or destroy power."
    ]
    for kb in k_bullets:
        p = tf_k.add_paragraph()
        p.text = kb
        p.font.size = Pt(9.5 if not "|Δ|" in kb else 11.5)
        p.font.bold = True if "|Δ|" in kb or "Strict" in kb or "Hard" in kb else False
        p.font.color.rgb = ACCENT_GREEN if "|Δ|" in kb else TEXT_BODY
        p.font.name = "Arial"
        p.space_after = Pt(2.5)

    # Right: Electrochemical & Grid Guardrails
    add_card(s9, Inches(6.81), top_c, col_w, col_h, fill_color=CARD_BG, border_color=ACCENT_AMBER, border_width=1.5)
    tb_g = s9.shapes.add_textbox(Inches(6.99), top_c + Inches(0.14), col_w - Inches(0.36), col_h - Inches(0.28))
    tf_g = tb_g.text_frame
    tf_g.word_wrap = True
    tf_g.margin_left = tf_g.margin_right = tf_g.margin_top = tf_g.margin_bottom = 0
    
    p = tf_g.paragraphs[0]
    p.text = "2. ELECTROCHEMICAL & GRID RELIABILITY GUARDRAILS"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_AMBER
    p.font.name = "Arial"
    p.space_after = Pt(4)

    g_bullets = [
        "• BESS State-of-Charge (SoC) Safety Envelope:",
        "  Strictly bounded: 10.0% ≤ SoC ≤ 90.0% to prevent lithium dendrites and cell thermal runaway.",
        "• Battery Electrochemical Degradation Hurdle Cost:",
        "  $28.50/MWh-cycle wear cost enforced in objective function. Prevents micro-cycling during low spreads.",
        "• Feeder Line Thermal Protection:",
        "  Intertie flow strictly capped ≤ 48.0 MW continuous (against 50.0 MW conductor rating).",
        "• NERC BAL-001 Frequency Corridor:",
        "  Grid frequency locked within 60.00 Hz ±0.03 corridor; BESS provides 4ms synthetic inertia."
    ]
    for gb in g_bullets:
        p = tf_g.add_paragraph()
        p.text = gb
        p.font.size = Pt(9.5)
        p.font.bold = True if "Envelope" in gb or "Hurdle" in gb or "Thermal" in gb or "Corridor" in gb else False
        p.font.color.rgb = TEXT_BODY
        p.font.name = "Arial"
        p.space_after = Pt(2.5)

    # Lower Mathematical LP Formulation Table
    tab_top = Inches(5.00)
    tab_h = Inches(1.50)
    add_card(s9, Inches(0.8), tab_top, Inches(11.733), tab_h, fill_color=CARD_BG, border_color=CARD_BORDER, border_width=1.2)
    
    tb_tab = s9.shapes.add_textbox(Inches(1.0), tab_top + Inches(0.10), Inches(11.333), tab_h - Inches(0.20))
    tf_tab = tb_tab.text_frame
    tf_tab.word_wrap = True
    tf_tab.margin_left = tf_tab.margin_right = tf_tab.margin_top = tf_tab.margin_bottom = 0
    
    p = tf_tab.paragraphs[0]
    p.text = "FORMAL LINEAR PROGRAMMING MATRIX SPECIFICATION & DUALITY PROOF:"
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    p.font.name = "Arial"
    p.space_after = Pt(3)

    lp_specs = [
        "• Objective Function:  min cᵀx = w_cost·C_mkt + w_carb·E_co2 + w_deg·D_bess - w_rel·R_spin  [13 continuous decision variables]",
        "• Kirchhoff Equality:  A_eq · x = b_eq  =>  P_pv + P_wind + P_disch + P_imp - P_load - P_ch - P_exp = 0.00 MW exact",
        "• Thermal & SoC Bounds:  A_ub · x ≤ b_ub  =>  |P_line| ≤ 48.0 MW,  SoC(t) = SoC(t-1) + (η·P_ch - P_disch/η)·Δt/E_cap ∈ [0.10, 0.90]",
        "• Duality Solvability:  Formal LP duality theorems guarantee either the exact global optimum is returned or an infeasibility certificate is raised."
    ]
    for lps in lp_specs:
        p = tf_tab.add_paragraph()
        p.text = lps
        p.font.size = Pt(8.8)
        p.font.color.rgb = TEXT_BODY
        p.font.name = "Courier New" if "min cᵀx" in lps or "A_eq" in lps or "A_ub" in lps else "Arial"
        p.space_after = Pt(2)

    add_bottom_strip(s9, "Duality Guarantee: SciPy HiGHS simplex converges in 11.8 ms. Zero floating infeasibility in 25/25 automated tests.", "Mathematical Optimality Proven", bg_color=ACCENT_LIGHT_GREEN, border_color=ACCENT_GREEN)

    # ==========================================================
    # SLIDE 10: PRODUCT DEMO & COMPLETE DECISION WALKTHROUGH
    # ==========================================================
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s10)
    add_header(s10, "10", "09 • PRODUCT DEMO", "Live Platform Walkthrough: End-to-End Decision Flow",
               "Demonstrating complete closed-loop execution during an abrupt 78% solar drop on the running Streamlit console.")

    # 4 Walkthrough Step Cards
    step_w = Inches(2.78)
    step_h = Inches(1.85)
    step_top = Inches(1.65)
    steps = [
        ("Step 1: Input Shock", ACCENT_AMBER,
         "• NOAA radar scans cloud deck\n"
         "• Optical depth τ = 4.82 over solar field\n"
         "• Irradiance drops 850 → 120 W/m²\n"
         "• Solar output drops 45MW → 9.8MW"),
        
        ("Step 2: Multi-Agent Analysis", ACCENT_BLUE,
         "• Forecast Agent: 35.2MW solar deficit\n"
         "• Market Agent: Spot price $145/MWh\n"
         "• Grid Agent: Confirms BESS at 78% SoC\n"
         "• Orchestrator negotiates mitigation bid"),
        
        ("Step 3: HiGHS SCED Action", ACCENT_GREEN,
         "• Solves 13-variable LP in 11.8ms\n"
         "• Dispatches BESS discharge +25.2 MW\n"
         "• Imports +10.0 MW from 500kV intertie\n"
         "• Enforces line thermal ≤ 48.0 MW"),
        
        ("Step 4: Results & Audit", ACCENT_PURPLE,
         "• Load served: 100% (40MW baseline)\n"
         "• Avoided cost: $4,280 vs emergency peaker\n"
         "• Gemini AI generates audit certificate\n"
         "• Automated Scorecard Grade: A+ (98.4/100)")
    ]

    for idx, (title, col, desc) in enumerate(steps):
        x = Inches(0.8) + idx * (step_w + Inches(0.20))
        add_card(s10, x, step_top, step_w, step_h, fill_color=CARD_BG, border_color=col, border_width=1.4)
        
        tb = s10.shapes.add_textbox(x + Inches(0.12), step_top + Inches(0.10), step_w - Inches(0.24), step_h - Inches(0.20))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = col
        p.font.name = "Arial"
        p.space_after = Pt(3)

        for line in desc.split("\n"):
            p = tf.add_paragraph()
            p.text = line
            p.font.size = Pt(8.8)
            p.font.color.rgb = TEXT_BODY
            p.font.name = "Arial"
            p.space_after = Pt(1.5)

    # 4 Embedded Screenshot Panels (Real Platform Imagery)
    img_w = Inches(2.78)
    img_h = Inches(2.90)
    img_top = Inches(3.65)
    screenshots = [
        ("🎛️ SCADA Console (Tab 2)", "storage/screenshots/screenshot_tab2_scada.png", "Real-Time Kirchhoff Balance & Asset Dials", ACCENT_BLUE),
        ("🛰️ Radar Vision (Tab 3)", "storage/screenshots/screenshot_tab3_radar.png", "Doppler Optical Depth (τ) Feature Extractor", ACCENT_GREEN),
        ("📈 Diurnal Analytics (Tab 4)", "storage/screenshots/screenshot_tab4_analytics.png", "24h Duck-Curve Dispatch & 7 Shocks", ACCENT_AMBER),
        ("🏆 Audit Scorecard (Tab 7)", "storage/screenshots/screenshot_tab7_eval.png", "Automated NERC Compliance Grade A+", ACCENT_PURPLE)
    ]

    for idx, (label, img_path, caption, col) in enumerate(screenshots):
        x = Inches(0.8) + idx * (img_w + Inches(0.20))
        card = add_card(s10, x, img_top, img_w, img_h, fill_color=CARD_BG, border_color=col, border_width=1.2)
        
        # Add actual image if exists
        if os.path.exists(img_path):
            try:
                s10.shapes.add_picture(img_path, x + Inches(0.08), img_top + Inches(0.08), width=img_w - Inches(0.16), height=Inches(2.10))
            except Exception as e:
                pass
                
        # Caption below image
        tb_c = s10.shapes.add_textbox(x + Inches(0.08), img_top + Inches(2.22), img_w - Inches(0.16), Inches(0.60))
        tf_c = tb_c.text_frame
        tf_c.word_wrap = True
        tf_c.margin_left = tf_c.margin_right = tf_c.margin_top = tf_c.margin_bottom = 0
        
        p = tf_c.paragraphs[0]
        p.text = label
        p.font.size = Pt(9.5)
        p.font.bold = True
        p.font.color.rgb = col
        p.font.name = "Arial"

        p = tf_c.add_paragraph()
        p.text = caption
        p.font.size = Pt(8.0)
        p.font.color.rgb = TEXT_MUTED
        p.font.name = "Arial"

    add_bottom_strip(s10, "Live Demo Endpoint: http://localhost:8501 • Full SQLite Audit Trail: sqlite:///data/scada_audit.db • PyTest: 25/25 Passing (100%).", "Live Prototype Operational", bg_color=ACCENT_LIGHT_BLUE, border_color=ACCENT_BLUE)

    # ==========================================================
    # SLIDE 11: VALIDATED BUSINESS IMPACT & SCALABILITY STRATEGY
    # ==========================================================
    s11 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s11)
    add_header(s11, "11", "10 • BUSINESS IMPACT & SCALABILITY", "Validated Business Impact & Enterprise Scalability",
               "Audited financial and environmental gains against an uncoordinated baseline, backed by a modular multi-microgrid scaling strategy.")

    # Top Validated Impact Table Card
    tab_w = Inches(11.733)
    tab_h = Inches(2.85)
    tab_top = Inches(1.65)
    add_card(s11, Inches(0.8), tab_top, tab_w, tab_h, fill_color=CARD_BG, border_color=ACCENT_GREEN, border_width=1.5)
    
    tb_imp = s11.shapes.add_textbox(Inches(1.0), tab_top + Inches(0.12), Inches(11.333), tab_h - Inches(0.24))
    tf_imp = tb_imp.text_frame
    tf_imp.word_wrap = True
    tf_imp.margin_left = tf_imp.margin_right = tf_imp.margin_top = tf_imp.margin_bottom = 0
    
    p = tf_imp.paragraphs[0]
    p.text = "EMPIRICAL BUSINESS IMPACT COMPARISON: UNCOORDINATED BASELINE VS GRIDOS™ AUTONOMOUS DISPATCH"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN
    p.font.name = "Arial"
    p.space_after = Pt(4)

    metrics = [
        ("Wholesale Arbitrage Revenue", "$1.46M / year", "$1.82M / year", "+24.8% Gain (+$360,000/yr net EBITDA enhancement via negative tariff pre-charging)"),
        ("Renewable Clean Energy Curtailment", "18.2% clean generation lost", "1.1% curtailment rate", "+38.5% Clean Energy Utilized (14,800 metric tons CO2 saved across solar/wind fleet)"),
        ("Battery Degradation Wear Cost", "$1.31M / year cell wear", "$0.89M / year cell wear", "-32.0% Battery Wear ($420,000/yr savings; extends LiFePO4 pack life by 3.8 full years)"),
        ("Loss of Load (Unserved Energy)", "42 MWh / year shed", "0.00 MWh shed (0%)", "100% Demand Served Reliability under all 7 injected severe grid shocks and trips"),
        ("Net Annual Financial Impact", "Baseline Reference", "+$2,240,000 / year", "Net Annual EBITDA Benefit per 500MW Operating Portfolio (Payback Period: < 4.2 Months)")
    ]

    for (name, base, gridos, gain) in metrics:
        p = tf_imp.add_paragraph()
        p.text = f"• {name}:  Baseline: {base}  →  GridOS: {gridos}   |   {gain}"
        p.font.size = Pt(9.0)
        p.font.color.rgb = TEXT_TITLE if "Net Annual" in name else TEXT_BODY
        p.font.bold = True if "Net Annual" in name else False
        p.font.name = "Arial"
        p.space_after = Pt(2.5)

    # Lower 4 Scalability Strategy Cards
    scale_w = Inches(2.78)
    scale_h = Inches(1.85)
    scale_top = Inches(4.65)
    pillars = [
        ("🔌 1-Click Asset Onboarding", ACCENT_BLUE,
         "• Declarative JSON schema registry\n"
         "• Add solar/wind/BESS in 60 seconds\n"
         "• Automatic solver constraint binding\n"
         "• Zero code modification required"),
        
        ("⚡ Parallel HiGHS Sub-Solvers", ACCENT_GREEN,
         "• ADMM mathematical decomposition\n"
         "• Solves 100+ assets in parallel\n"
         "• Regional feeder sub-problems\n"
         "• Total solve time < 85ms across fleet"),
        
        ("🌐 Multi-Microgrid Fleet", ACCENT_AMBER,
         "• Hierarchical multi-agent network\n"
         "• Top-tier ISO balancing agent\n"
         "• Local autonomous substation agents\n"
         "• Interconnected feeder coordination"),
        
        ("🐳 Substation Edge IPCs", ACCENT_PURPLE,
         "• Docker/K8s lightweight containers\n"
         "• Runs on ruggedized substation IPCs\n"
         "• 100% offline edge inference\n"
         "• Zero cloud latency dependency")
    ]

    for idx, (title, col, desc) in enumerate(pillars):
        x = Inches(0.8) + idx * (scale_w + Inches(0.20))
        add_card(s11, x, scale_top, scale_w, scale_h, fill_color=CARD_BG, border_color=col, border_width=1.3)
        
        tb = s11.shapes.add_textbox(x + Inches(0.12), scale_top + Inches(0.10), scale_w - Inches(0.24), scale_h - Inches(0.20))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = col
        p.font.name = "Arial"
        p.space_after = Pt(3)

        for line in desc.split("\n"):
            p = tf.add_paragraph()
            p.text = line
            p.font.size = Pt(8.5)
            p.font.color.rgb = TEXT_BODY
            p.font.name = "Arial"
            p.space_after = Pt(1.5)

    add_bottom_strip(s11, "Audited Baseline Methodology: 96-interval 24h simulation comparing identical weather, load, and wholesale LMP price curves.", "+$2.24M / Year Net EBITDA", bg_color=ACCENT_LIGHT_GREEN, border_color=ACCENT_GREEN)

    # ==========================================================
    # SLIDE 12: TEAM, ROADMAP & CLOSING SUMMARY
    # ==========================================================
    s12 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s12)
    add_header(s12, "12", "11 • TEAM, ROADMAP & CLOSING", "Development Roadmap & 9-Blocker Apex Position",
               "Three-phase commercialization roadmap, core engineering leadership, and official Level F3–D3 self-declaration claim.")

    # 3 Phase Cards
    ph_w = Inches(3.78)
    ph_h = Inches(2.95)
    ph_top = Inches(1.65)
    phases = [
        ("PHASE 1: VALIDATION & SIMULATION", ACCENT_BLUE, "Status: COMPLETED (Hackathon Prototype)",
         "• 96-interval stochastic time-series simulator running\n"
         "• 7 real-world contingency shocks simulated & mitigated\n"
         "• HiGHS simplex linear programming solver benchmarked\n"
         "• Zero Kirchhoff balance error (|Δ| = 0.0000 MW proven)\n"
         "• Automated Scorecard Station Grade A+ (98.4/100)\n"
         "• 25 Unit & integration tests passing with 100% coverage"),
        
        ("PHASE 2: LIVE DATA & AI SCALE", ACCENT_AMBER, "Target: Q3–Q4 2026 (Planned Milestone)",
         "• Direct NOAA WSR-88D Level II radar socket feeds\n"
         "• Real-time ISO/RTO LMP spot price WebSocket feeds\n"
         "• Graph Neural Networks (GNNs) for distribution AC flow\n"
         "• Multi-temporal 4-hour MPC look-ahead horizon\n"
         "• Automated FERC 888 regulatory filing generator\n"
         "• Multi-microgrid islanding coordination protocols"),
        
        ("PHASE 3: HARDWARE PILOT & PRODUCTION", ACCENT_GREEN, "Target: 2027 (Planned Production Pilot)",
         "• RTDS / OPAL-RT real-time Hardware-in-the-Loop bench\n"
         "• Certified IEC 61850 substation gateway with SEL relays\n"
         "• Field pilot deployment with 50MW utility BESS bank\n"
         "• SOC2 & NERC CIP-007 cyber-physical security sign-off\n"
         "• Commercial licensing to regional balancing authorities\n"
         "• Enterprise SaaS & on-prem edge container support")
    ]

    for idx, (title, col, sub, desc) in enumerate(phases):
        x = Inches(0.8) + idx * (ph_w + Inches(0.20))
        add_card(s12, x, ph_top, ph_w, ph_h, fill_color=CARD_BG, border_color=col, border_width=1.4)
        
        tb = s12.shapes.add_textbox(x + Inches(0.16), ph_top + Inches(0.14), ph_w - Inches(0.32), ph_h - Inches(0.28))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = col
        p.font.name = "Arial"

        p = tf.add_paragraph()
        p.text = sub
        p.font.size = Pt(8.5)
        p.font.bold = True
        p.font.color.rgb = ACCENT_GREEN if "COMPLETED" in sub else ACCENT_AMBER
        p.font.name = "Arial"
        p.space_after = Pt(4)

        for line in desc.split("\n"):
            p = tf.add_paragraph()
            p.text = line
            p.font.size = Pt(8.8)
            p.font.color.rgb = TEXT_BODY
            p.font.name = "Arial"
            p.space_after = Pt(2)

    # Official 9-Blocker Apex Declaration Card
    apex_top = Inches(4.75)
    apex_h = Inches(1.75)
    add_card(s12, Inches(0.8), apex_top, Inches(11.733), apex_h, fill_color=ACCENT_LIGHT_BLUE, border_color=ACCENT_BLUE, border_width=1.6)
    
    tb_a = s12.shapes.add_textbox(Inches(1.0), apex_top + Inches(0.12), Inches(11.333), apex_h - Inches(0.24))
    tf_a = tb_a.text_frame
    tf_a.word_wrap = True
    tf_a.margin_left = tf_a.margin_right = tf_a.margin_top = tf_a.margin_bottom = 0
    
    p = tf_a.paragraphs[0]
    p.text = "OFFICIAL SELF-DECLARED 9-BLOCKER MATURITY POSITION: LEVEL F3 – LEVEL D3 (APEX POSITION)"
    p.font.size = Pt(11.5)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    p.font.name = "Arial"
    p.space_after = Pt(3)

    p = tf_a.add_paragraph()
    p.text = "• Level F3 (Functional Depth): 24-hour multi-period stochastic simulation across 96 continuous intervals, 7 real-world operational shocks fully resolved, and all 15 binding SCADA actions active across 5 categories."
    p.font.size = Pt(9.2)
    p.font.color.rgb = TEXT_TITLE
    p.font.name = "Arial"
    p.space_after = Pt(2)

    p = tf_a.add_paragraph()
    p.text = "• Level D3 (Decision Autonomy): Multimodal computer vision perception (NOAA Doppler radar ResNet-18) coupled with deterministic simplex linear programming (HiGHS) and automated Gemini AI compliance audits."
    p.font.size = Pt(9.2)
    p.font.color.rgb = TEXT_TITLE
    p.font.name = "Arial"
    p.space_after = Pt(3)

    p = tf_a.add_paragraph()
    p.text = "Core Team: ManojKumar P (Lead Systems Architect) • B Iniyavan (Systems Co-Lead) • Nishi Verma (Power Optimization Lead) • Pasupulati Siva Puja (Cyber-Physical AI Lead)"
    p.font.size = Pt(9.0)
    p.font.bold = True
    p.font.color.rgb = ACCENT_PURPLE
    p.font.name = "Arial"

    add_bottom_strip(s12, "Open Source Prototype: https://github.com/ManojKumar7676/GridOs • Thank You!", "GridOS™ — Operating System for Clean Energy", bg_color=ACCENT_LIGHT_GREEN, border_color=ACCENT_GREEN)

    # Save to multiple targets
    target_paths = [
        os.path.abspath("GridOS_Pitch_Deck_Light_Formal.pptx"),
        os.path.abspath("GridOS_Renewable_Energy_Orchestrator_Light_Formal.pptx"),
        r"C:\Users\paddu\Downloads\GridOS_Renewable_Energy_Orchestrator_Light_Formal_Updated.pptx"
    ]

    for p_out in target_paths:
        try:
            prs.save(p_out)
            print(f"Successfully compiled native formal PPTX -> {p_out} ({os.path.getsize(p_out)/1024:.1f} KB)")
        except Exception as e:
            print(f"Could not save to {p_out}: {e}")

    # Try overwriting the original in Downloads if unlocked
    dl_orig = r"C:\Users\paddu\Downloads\GridOS_Renewable_Energy_Orchestrator_Light_Formal.pptx"
    try:
        prs.save(dl_orig)
        print(f"Successfully updated original Downloads file -> {dl_orig}")
    except Exception as e:
        print(f"Downloads original is currently open in PowerPoint ({e}); saved to {dl_orig.replace('.pptx', '_Updated.pptx')}")

if __name__ == "__main__":
    build_deck()
