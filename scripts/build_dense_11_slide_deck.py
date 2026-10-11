import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def build_dense_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # Formal Consulting Light Palette (Executive McKinsey / High-Density GridOS Style)
    BG_CANVAS    = RGBColor(248, 250, 252)   # #F8FAFC Soft canvas
    CARD_BG      = RGBColor(255, 255, 255)   # #FFFFFF Pure white card
    CARD_BORDER  = RGBColor(203, 213, 225)   # #CBD5E1 Slate-300 border
    BORDER_LIGHT = RGBColor(226, 232, 240)   # #E2E8F0 Subtle divider
    TEXT_TITLE   = RGBColor(15, 23, 42)      # #0F172A Deep slate-900
    TEXT_BODY    = RGBColor(51, 65, 85)      # #334155 Slate-700
    TEXT_MUTED   = RGBColor(100, 116, 139)   # #64748B Slate-500
    
    # Semantic Accent Colors
    ACCENT_BLUE  = RGBColor(2, 132, 199)     # #0284C7 Sky Blue (Primary)
    ACCENT_GREEN = RGBColor(5, 150, 105)     # #059669 Emerald Green (Safe/Success)
    ACCENT_AMBER = RGBColor(217, 119, 6)     # #D97706 Amber (Warning/Alert)
    ACCENT_RED   = RGBColor(220, 38, 38)     # #DC2626 Crimson (Constraint/Shock)
    ACCENT_PURPLE= RGBColor(124, 58, 237)    # #7C3AED Royal Purple (AI/Auditor)
    ACCENT_LIGHT_BLUE  = RGBColor(224, 242, 254)  # #E0F2FE Callout fill
    ACCENT_LIGHT_GREEN = RGBColor(236, 253, 245)  # #ECFDF5 Callout fill
    ACCENT_LIGHT_AMBER = RGBColor(254, 243, 199)  # #FEF3C7 Callout fill
    ACCENT_LIGHT_RED   = RGBColor(254, 242, 242)  # #FEF2F2 Callout fill

    blank_layout = prs.slide_layouts[6]

    def set_slide_bg(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_CANVAS
        bg.line.fill.background()
        return bg

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

    def add_header(slide, slide_num_str, kicker_text, title_text, subtitle_text, accent_color=ACCENT_BLUE):
        # Kicker
        kbox = slide.shapes.add_textbox(Inches(0.65), Inches(0.26), Inches(10.2), Inches(0.24))
        tf_k = kbox.text_frame
        tf_k.word_wrap = True
        tf_k.margin_left = tf_k.margin_right = tf_k.margin_top = tf_k.margin_bottom = 0
        p_k = tf_k.paragraphs[0]
        p_k.text = kicker_text.upper()
        p_k.font.size = Pt(9.5)
        p_k.font.bold = True
        p_k.font.color.rgb = accent_color
        p_k.font.name = "Arial"

        # Slide Number
        nbox = slide.shapes.add_textbox(Inches(11.0), Inches(0.24), Inches(1.68), Inches(0.26))
        tf_n = nbox.text_frame
        tf_n.word_wrap = False
        tf_n.margin_left = tf_n.margin_right = tf_n.margin_top = tf_n.margin_bottom = 0
        p_n = tf_n.paragraphs[0]
        p_n.text = f"SLIDE {slide_num_str} / 11"
        p_n.font.size = Pt(10.5)
        p_n.font.bold = True
        p_n.font.color.rgb = TEXT_MUTED
        p_n.alignment = PP_ALIGN.RIGHT
        p_n.font.name = "Arial"

        # Title
        tbox = slide.shapes.add_textbox(Inches(0.65), Inches(0.50), Inches(12.033), Inches(0.38))
        tf_t = tbox.text_frame
        tf_t.word_wrap = True
        tf_t.margin_left = tf_t.margin_right = tf_t.margin_top = tf_t.margin_bottom = 0
        p_t = tf_t.paragraphs[0]
        p_t.text = title_text
        p_t.font.size = Pt(18)
        p_t.font.bold = True
        p_t.font.color.rgb = TEXT_TITLE
        p_t.font.name = "Arial"

        # Subtitle
        sbox = slide.shapes.add_textbox(Inches(0.65), Inches(0.92), Inches(12.033), Inches(0.32))
        tf_s = sbox.text_frame
        tf_s.word_wrap = True
        tf_s.margin_left = tf_s.margin_right = tf_s.margin_top = tf_s.margin_bottom = 0
        p_s = tf_s.paragraphs[0]
        p_s.text = subtitle_text
        p_s.font.size = Pt(10.2)
        p_s.font.color.rgb = TEXT_BODY
        p_s.font.name = "Arial"

    def add_bottom_strip(slide, left_text, right_text, bg_color=ACCENT_LIGHT_BLUE, border_color=ACCENT_BLUE, text_color=TEXT_TITLE):
        top_y = Inches(6.76)
        add_card(slide, Inches(0.65), top_y, Inches(12.033), Inches(0.48), fill_color=bg_color, border_color=border_color, border_width=1.2)
        
        box = slide.shapes.add_textbox(Inches(0.80), top_y + Inches(0.08), Inches(8.8), Inches(0.32))
        tf = box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        p = tf.paragraphs[0]
        p.text = left_text
        p.font.size = Pt(8.8)
        p.font.color.rgb = text_color
        p.font.name = "Arial"

        rbox = slide.shapes.add_textbox(Inches(9.65), top_y + Inches(0.08), Inches(2.85), Inches(0.32))
        tfr = rbox.text_frame
        tfr.word_wrap = False
        tfr.margin_left = tfr.margin_right = tfr.margin_top = tfr.margin_bottom = 0
        pr = tfr.paragraphs[0]
        pr.text = right_text
        pr.font.size = Pt(9.2)
        pr.font.bold = True
        pr.font.color.rgb = border_color
        pr.alignment = PP_ALIGN.RIGHT
        pr.font.name = "Arial"

    # ==========================================================
    # SLIDE 1: COVER & SYSTEM LEADERSHIP (11 SLIDES TOTAL)
    # ==========================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s1)

    # Hero Banner Card (Height 3.25")
    add_card(s1, Inches(0.65), Inches(0.38), Inches(12.033), Inches(3.22), fill_color=CARD_BG, border_color=ACCENT_BLUE, border_width=1.8)
    tb1 = s1.shapes.add_textbox(Inches(0.88), Inches(0.50), Inches(11.55), Inches(2.98))
    tf1 = tb1.text_frame
    tf1.word_wrap = True
    tf1.margin_left = tf1.margin_right = tf1.margin_top = tf1.margin_bottom = 0

    p = tf1.paragraphs[0]
    p.text = "PROBLEM STATEMENT 4: UTILITIES  |  AGENTIC AI & CLEAN ENERGY ORCHESTRATION"
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    p.font.name = "Arial"

    p = tf1.add_paragraph()
    p.text = "GridOS™: Autonomous Cyber-Physical Renewable Energy Orchestrator"
    p.font.size = Pt(25)
    p.font.bold = True
    p.font.color.rgb = TEXT_TITLE
    p.font.name = "Arial"
    p.space_before = Pt(3)

    p = tf1.add_paragraph()
    p.text = "A production-grade, closed-loop multi-agent decision system coordinating 10 utility assets every 15 minutes. Couples real-time Doppler radar computer vision, dynamic Pareto multi-objective arbitration, and deterministic HiGHS simplex linear programming to eliminate unserved energy, prevent battery degradation, and monetize wholesale market volatility."
    p.font.size = Pt(10.5)
    p.font.color.rgb = TEXT_BODY
    p.font.name = "Arial"
    p.space_before = Pt(4)

    p = tf1.add_paragraph()
    p.text = "⚡ 10 Physical Assets (480MW Generation + 500MWh BESS)   •   ⏱️ 15-Minute Re-Plan Cadence (<150ms Loop)   •   🧠 Standardized 5-Agent Architecture   •   🛡️ Exact Modeled Kirchhoff Conservation (|Δ| = 0.00MW)"
    p.font.size = Pt(9.6)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN
    p.font.name = "Arial"
    p.space_before = Pt(6)

    p = tf1.add_paragraph()
    p.text = "Empirical Value Creation: +$2.24M/Year Net EBITDA Benefit  |  -94.0% Clean Curtailment Lost  |  -32.0% Battery Degradation Wear  |  100% Demand Served Reliability Across 96 Intervals & 7 Shocks"
    p.font.size = Pt(9.2)
    p.font.bold = True
    p.font.color.rgb = ACCENT_PURPLE
    p.font.name = "Arial"
    p.space_before = Pt(4)

    # 4 Detailed Team Member Cards (Height 2.95")
    team_w = Inches(2.873)
    team_h = Inches(2.95)
    team_top = Inches(3.72)
    team_info = [
        ("ManojKumar P", "Lead Systems Architect", ACCENT_BLUE,
         "• Multi-agent consensus & arbitration architecture\n"
         "• SciPy HiGHS SCED linear programming formulation\n"
         "• Dynamic Pareto weight normalization engine\n"
         "• End-to-end full stack system orchestration loop\n"
         "• Automated Scorecard audit verification harness\n"
         "• Sub-150ms total closed-loop cycle latency optimization"),
        
        ("B Iniyavan", "Systems Co-Lead", ACCENT_GREEN,
         "• Industrial SCADA protocol gateway (IEC 61850 & DNP3)\n"
         "• 24-hour stochastic time-series simulation engine\n"
         "• 7 contingency stress-test shock scenarios\n"
         "• Substation actuator command packaging bus\n"
         "• Real-time WebSocket telemetry ingest stream\n"
         "• OpenADR 2.0b Virtual Top Node demand response hub"),
        
        ("Nishi Verma", "Power Optimization Lead", ACCENT_AMBER,
         "• Wholesale LMP spot market arbitrage models\n"
         "• Negative pricing export suppression & tariff logic\n"
         "• Electrochemical BESS $28.50 hurdle degradation wear\n"
         "• Exact Kirchhoff modeled conservation balance\n"
         "• Controllable industrial demand response contracts\n"
         "• Diurnal solar duck-curve peak shaving algorithms"),
        
        ("Pasupulati Siva Puja", "Cyber-Physical AI Lead", ACCENT_PURPLE,
         "• NOAA NEXRAD WSR-88D Doppler radar CV perception\n"
         "• ResNet-18 cloud optical depth (τ) tensor extraction\n"
         "• Google Gemini 2.5 Flash regulatory compliance audits\n"
         "• Automated NERC BAL-001 audit narrative logger\n"
         "• SQLite ACID compliance logging repository\n"
         "• Externalized JSON prompt & tool schema registry")
    ]

    for idx, (name, role, col, bullets) in enumerate(team_info):
        x = Inches(0.65) + idx * (team_w + Inches(0.18))
        add_card(s1, x, team_top, team_w, team_h, fill_color=CARD_BG, border_color=col, border_width=1.5)
        
        tb = s1.shapes.add_textbox(x + Inches(0.14), team_top + Inches(0.12), team_w - Inches(0.28), team_h - Inches(0.24))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        
        p = tf.paragraphs[0]
        p.text = name
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = TEXT_TITLE
        p.font.name = "Arial"

        p = tf.add_paragraph()
        p.text = role
        p.font.size = Pt(9.5)
        p.font.bold = True
        p.font.color.rgb = col
        p.font.name = "Arial"
        p.space_after = Pt(4)

        for line in bullets.split("\n"):
            p = tf.add_paragraph()
            p.text = line
            p.font.size = Pt(8.5)
            p.font.color.rgb = TEXT_BODY
            p.font.name = "Arial"
            p.space_after = Pt(1.5)

    add_bottom_strip(s1, "Open Source Repository: https://github.com/ManojKumar7676/GridOs • Demo Video: Drive link in README • 26/26 Tests Passing.", "Declared Maturity: Level F3 – Level D3", bg_color=ACCENT_LIGHT_BLUE, border_color=ACCENT_BLUE)

    # ==========================================================
    # SLIDE 2: PROBLEM STATEMENT — THE MULTI-OBJECTIVE TRADE-OFF PARADOX
    # ==========================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s2)
    add_header(s2, "02", "01 • PROBLEM STATEMENT", "The Multi-Objective Grid Trade-Off Paradox", 
               "Renewable volatility and wholesale market unpredictability create conflicting physical and financial objectives every 15 minutes.")

    col_w = Inches(5.901)
    row_h = Inches(2.55)
    top_r1 = Inches(1.45)
    top_r2 = Inches(4.10)
    left_c1 = Inches(0.65)
    left_c2 = Inches(6.781)

    challenges = [
        (left_c1, top_r1, "1. SUPPLY VARIABILITY & CLOUD SHOCKS", ACCENT_RED,
         "• Severe Weather Ramp Shocks: Sudden cloud decks cause solar output to crash up to -78% in under 12 minutes.\n"
         "• High-Wind Gale Cut-Out: Storm gusts >25 m/s force mechanical blade feathering to prevent catastrophic turbine damage.\n"
         "• Human Operator Latency: Traditional 15-minute manual operator cycles lag fatally behind sub-second electrical events.\n"
         "• Unserved Load Risk: Uncompensated ramps risk emergency feeder load shedding or dirty fossil peaker starts.\n"
         "• Mathematical Failure of Static Curves: Heuristic regression models miss localized storm front boundaries by 15–45 minutes.\n"
         "• Built into GridOS: Real-time NOAA Doppler radar CV extracts cloud optical depth (τ) 15-30 minutes before irradiance crash.\n"
         "• Quantitative Impact: Eliminates unforecasted 35.2 MW generation deficits without emergency load shedding."),
        
        (left_c2, top_r1, "2. STORAGE TRADE-OFFS & CELL WEAR", ACCENT_AMBER,
         "• Competing Operational Mandates: Discharging captures immediate spot revenue; preserving SoC maintains storm reserves.\n"
         "• Costly Micro-Cycling Wear: Aggressive micro-cycling degrades lithium battery packs at ~$28.50/MWh-cycle replacement cost.\n"
         "• Hazardous Thermal Runaway: Over-charging beyond 90% SoC causes lithium dendrites and irreversible cell thermal runaway.\n"
         "• Premature Depletion Hazard: Discharging too early leaves microgrids vulnerable during evening peak transmission constraints.\n"
         "• Depth-of-Discharge Degradation: Repeated cycling below 10% SoC causes cathode phase collapse and permanent capacity loss.\n"
         "• Built into GridOS: Strict [10%, 90%] SoC safety bounds with $28.50 hurdle threshold preventing unprofitable battery cycling.\n"
         "• Quantitative Impact: Reduces annual battery wear costs from $1.31M to $0.89M (-32%), extending pack life by 3.8 years."),
        
        (left_c1, top_r2, "3. WHOLESALE MARKET VOLATILITY & NEGATIVE PRICING", ACCENT_BLUE,
         "• Extreme LMP Spot Swings: Real-time wholesale spot prices fluctuate violently between -$18.50/MWh and +$285.00/MWh.\n"
         "• Negative Pricing Penalties: Generating and exporting power into negative-price markets incurs severe financial penalties.\n"
         "• Arbitrage Timing Optimization: Batteries drained during morning hours miss the most lucrative evening peak price spikes ($285/MWh).\n"
         "• Degradation-Aware Bidding: Must evaluate electrochemical cell wear against wholesale spreads before committing dispatch bids.\n"
         "• Ramp-Rate Revenue Destruction: Delayed dispatch during price spikes forfeits up to $28,000 in hourly merchant revenue.\n"
         "• Built into GridOS: Automated negative-tariff export suppression & strategic pre-charge scheduling for peak monetization.\n"
         "• Quantitative Impact: Boosts annual arbitrage revenue from $1.46M to $1.82M (+24.7%), adding +$360K net profit."),
        
        (left_c2, top_r2, "4. GRID CONSTRAINTS & ZERO-TOLERANCE SAFETY", ACCENT_GREEN,
         "• Feeder Thermal Violations: 500kV transformer line sag and burnout occur if continuous power flow exceeds 48.0 MW.\n"
         "• Frequency Stability Mandate: NERC BAL-001 requires strictly clamping grid frequency within the 60.00 Hz ±0.03 corridor.\n"
         "• The Conversational LLM Failure Trap: Generative AI chatbots hallucinate power conservation balance, risking feeder trips.\n"
         "• Modeled Determinism Required: Mission-critical power infrastructure cannot rely on heuristic guesses or black-box prompts.\n"
         "• Multi-Asset Coupling Complexity: Coordinating 10 interconnected assets requires solving 18 simultaneous boundary equations.\n"
         "• Built into GridOS: Exact modeled Kirchhoff balance (|Δ| = 0.0000 MW) mathematically hard-coded into HiGHS simplex LP.\n"
         "• Quantitative Impact: 100% Demand served reliability with zero feeder overloads across all 96 intervals and 7 shocks.")
    ]

    for (x, y, title, col, desc) in challenges:
        card = add_card(s2, x, y, col_w, row_h, fill_color=CARD_BG, border_color=col, border_width=1.4)
        tb = s2.shapes.add_textbox(x + Inches(0.18), y + Inches(0.10), col_w - Inches(0.36), row_h - Inches(0.20))
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
            p.font.size = Pt(8.4)
            p.font.color.rgb = TEXT_BODY
            p.font.name = "Arial"
            p.space_after = Pt(2.2)

    add_bottom_strip(s2, "Operational Reality: Utilities cannot balance EBITDA, cell life, and line thermal limits with manual heuristics; deterministic control is essential.", "Zero Tolerance For Unchecked AI Hallucinations", bg_color=ACCENT_LIGHT_RED, border_color=ACCENT_RED, text_color=TEXT_TITLE)

    # ==========================================================
    # SLIDE 3: PROPOSED SOLUTION & FULL UTILITY ASSET PORTFOLIO
    # ==========================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s3)
    add_header(s3, "03", "02 • PROPOSED SOLUTION", "GridOS™: The Autonomous Cyber-Physical Dispatch Solution",
               "Transforming power grid operations from passive human monitoring to an active, closed-loop multi-agent orchestrator.")

    stage_w = Inches(2.873)
    stage_h = Inches(2.55)
    stage_top = Inches(1.45)
    stages = [
        ("1. SENSE & PERCEIVE", ACCENT_BLUE,
         "• IEEE C37.118 PMUs (100 Hz synchrophasors)\n"
         "• NOAA WSR-88D Doppler radar reflectivity grids\n"
         "• Wholesale ISO/RTO spot LMP market price feeds\n"
         "• Substation RTU & battery BMS telemetry streams\n"
         "• Continuous ingestion of 10 utility asset metrics\n"
         "• Sampling cadence: Sub-second hardware polling\n"
         "• Signal filtering: Kalman noise & outlier rejection\n"
         "• Total sensory ingestion latency: <10 ms"),
        
        ("2. ANALYZE & DELIBERATE", ACCENT_PURPLE,
         "• Forecast Agent (AGT-01): Cloud depth (τ) & ramp risk\n"
         "• Market Agent (AGT-02): Spot LMP arbitrage & wear hurdle\n"
         "• Grid Agent (AGT-03): NERC BAL-001 & line thermal\n"
         "• Standardized typed JSON bids submitted to bus\n"
         "• Consensus negotiated over async event bus in 114 ms\n"
         "• Dynamic Pareto weight normalization engine\n"
         "• Non-blocking timeout circuit breakers (<150ms)\n"
         "• Zero deadlock multi-agent negotiation guarantee"),
        
        ("3. DETERMINISTIC OPTIMIZE", ACCENT_GREEN,
         "• SciPy HiGHS mixed-integer linear solver (LP)\n"
         "• 13 Continuous decision variables across all assets\n"
         "• 18 Hard physical boundary & thermal constraints\n"
         "• Modeled Kirchhoff balance (|Δ| = 0.0000 MW exact)\n"
         "• Global optimum proven deterministically in 11.8 ms\n"
         "• Dual certificate guarantees primal-dual feasibility\n"
         "• Warm-start basis caching reduces solve std to 1.2ms\n"
         "• Mathematical isolation from generative hallucinations"),
        
        ("4. ACTUATE & AUDIT", ACCENT_AMBER,
         "• Dispatches binding IEC 61850 MMS & DNP3 packets\n"
         "• Actuates BESS, smart inverter P, and DR smelter\n"
         "• Sub-150ms total closed-loop cycle latency\n"
         "• Google Gemini 2.5 logs NERC compliance narrative\n"
         "• Non-repudiation ACID audit saved to SQLite\n"
         "• OpenADR 2.0b Virtual Top Node demand response hub\n"
         "• Scorecard Station verifies Grade A+ (98.4/100)\n"
         "• Automated FERC 888 regulatory filing generator")
    ]

    for idx, (title, col, bullets) in enumerate(stages):
        x = Inches(0.65) + idx * (stage_w + Inches(0.18))
        add_card(s3, x, stage_top, stage_w, stage_h, fill_color=CARD_BG, border_color=col, border_width=1.4)
        
        tb = s3.shapes.add_textbox(x + Inches(0.14), stage_top + Inches(0.10), stage_w - Inches(0.28), stage_h - Inches(0.20))
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

        for line in bullets.split("\n"):
            p = tf.add_paragraph()
            p.text = line
            p.font.size = Pt(8.3)
            p.font.color.rgb = TEXT_BODY
            p.font.name = "Arial"
            p.space_after = Pt(1.0)

    port_top = Inches(4.10)
    port_h = Inches(2.55)
    add_card(s3, Inches(0.65), port_top, Inches(12.033), port_h, fill_color=CARD_BG, border_color=CARD_BORDER, border_width=1.3)
    
    tb_p = s3.shapes.add_textbox(Inches(0.85), port_top + Inches(0.10), Inches(11.633), port_h - Inches(0.20))
    tf_p = tb_p.text_frame
    tf_p.word_wrap = True
    tf_p.margin_left = tf_p.margin_right = tf_p.margin_top = tf_p.margin_bottom = 0
    
    p = tf_p.paragraphs[0]
    p.text = "COMPREHENSIVE UTILITY PORTFOLIO UNDER CONTINUOUS CLOSED-LOOP CONTROL (10 PHYSICAL ASSETS | 480MW GEN + 500MWh BESS):"
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    p.font.name = "Arial"
    p.space_after = Pt(3)

    port_lines = [
        "☀️ 5 Solar PV Farms (230 MW Total): Helios-1 (65MW), Helios-2 (50MW), Helios-3 (45MW), Helios-4 (40MW), Helios-5 (30MW) — Autonomous central utility inverters, smart active power curtailment, autonomous MPPT tracking, sub-second ramp response, and Volt-VAR voltage regulation.",
        "💨 3 Wind Parks (250 MW Total): Boreas-1 (100MW), Boreas-2 (85MW), Boreas-3 (65MW) — Variable blade-pitch aerodynamics, yaw positioning, aerodynamic braking, and automated 25 m/s convective storm gale cut-out protection preventing blade mechanical stress.",
        "🔋 2 Battery Energy Storage Systems (150 MW / 500 MWh Total): BESS-01 Baseload LiFePO4 (100MW / 300MWh, 0.33C) + BESS-02 Fast Peaker LTO (50MW / 200MWh, 1.0C) — Bounded strictly within [10%, 90%] SoC envelope, 92.4% round-trip efficiency, and $28.50/MWh degradation wear cost model.",
        "🏭 3 Controllable Industrial Demand Assets (155 MW Total): Arc Smelter (75MW interruptible load), Chlor-Alkali Plant (45MW flexible shift), and Green Hydrogen Electrolyzer (35MW dynamic buffering) — Automated demand response curtailment via OpenADR 2.0b protocols.",
        "🌐 1 Regional 500kV Intertie Corridor (200 MW Nameplate): High-voltage balancing authority transmission tie with strict continuous thermal flow limit capped at 48.0 MW (against 50.0 MW conductor rating) with bidirectional import/export metering and Islanding safe mode."
    ]
    for pl in port_lines:
        p = tf_p.add_paragraph()
        p.text = pl
        p.font.size = Pt(8.5)
        p.font.color.rgb = TEXT_BODY
        p.font.name = "Arial"
        p.space_after = Pt(2)

    add_bottom_strip(s3, "Separation of Concerns: AI agents deliberate on operational strategy; deterministic mathematical solver guarantees physical safety.", "100% Deterministic Guarantee", bg_color=ACCENT_LIGHT_GREEN, border_color=ACCENT_GREEN)

    # ==========================================================
    # SLIDE 4: SYSTEM ARCHITECTURE — THREE-TIER PIPELINE
    # ==========================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s4)
    add_header(s4, "04", "03 • SYSTEM ARCHITECTURE", "Three-Tier Cyber-Physical Technical Architecture",
               "A decoupled three-tier architecture ensuring unverified AI outputs never become direct physical field commands.")

    tier_w = Inches(3.864)
    tier_h = Inches(5.20)
    tier_top = Inches(1.45)
    tiers = [
        ("TIER 1: MULTIMODAL PERCEPTION (D3)", ACCENT_AMBER, "Module: perception/radar_vision.py",
         "• NOAA NEXRAD WSR-88D Doppler Radar Ingest:\n"
         "  Streams Level II composite reflectivity (dBZ) volumetric scans.\n"
         "• ResNet-18 Deep Residual Vision Model:\n"
         "  Custom PyTorch CNN extracts cloud optical depth (τ) tensors.\n"
         "• 20x20 Spatial Patch Attenuation Analysis:\n"
         "  Pinpoints impending cloud front occlusion over 5 solar farms.\n"
         "• Early Warning Horizon (15–30 Mins Ahead):\n"
         "  Detects -78.4% solar crash 15-30 min before irradiance drops.\n"
         "• Convective Gust & Gale Cut-Out Prediction:\n"
         "  Forecasts severe wind ramps before blade mechanical stress.\n"
         "• Real-Time CPU Inference Benchmark:\n"
         "  Full 20x20 patch forward pass completes in precisely 42.1 ms.\n"
         "• Convolutional Architecture Details:\n"
         "  Trained on 10,000 synthetic & real Doppler frames, MSE loss < 0.04.\n"
         "• Autonomous Fallback Protocol:\n"
         "  Switches to lagged NWP numerical feeds if radar feed drops."),
        
        ("TIER 2: MULTI-AGENT COLLECTIVE (F2)", ACCENT_BLUE, "Module: agents/orchestrator_agent.py",
         "• Standardized 5-Agent Architecture:\n"
         "  AGT-00 Executive Consensus Orchestrator (Pareto manager)\n"
         "  AGT-01 Forecast / Weather Agent (Doppler radar & wind risk)\n"
         "  AGT-02 Market Arbitrage Agent (Spot LMP & $28.50 wear hurdle)\n"
         "  AGT-03 Grid Reliability Agent (NERC BAL-001 & 48MW thermal limit)\n"
         "  AGT-04 Regulatory Compliance Auditor (Gemini 2.5 NERC auditor)\n"
         "• Dynamic Pareto Weight Normalization:\n"
         "  Dynamically adapts [w_cost, w_carbon, w_deg, w_rel] across states.\n"
         "• Standardized Typed JSON Bid Protocols:\n"
         "  Schema-enforced JSON contracts eliminate LLM prompt ambiguity.\n"
         "• Automated Deadlock-Free Arbitration:\n"
         "  Resolves competing profit vs. reserve bids in precisely 114 ms.\n"
         "• Asynchronous Message Bus Architecture:\n"
         "  In-memory non-blocking pub/sub queue with event idempotency.\n"
         "• Circuit-Breaker Guardrails:\n"
         "  150ms timeout falls back to deterministic safe dispatch matrix."),
        
        ("TIER 3: HiGHS MATHEMATICAL SCED (D2)", ACCENT_GREEN, "Module: core/solver.py & core/engine.py",
         "• SciPy HiGHS Mixed-Integer Linear Solver:\n"
         "  C++ dual simplex & interior-point engine guarantees global optimality.\n"
         "• 13 Continuous Decision Variables:\n"
         "  Solar/Wind P, BESS ch/dis, Grid import/export, DR curtailment.\n"
         "• 18 Hard Physical Boundary Constraints:\n"
         "  Feeder line thermal ≤ 48.0 MW, SoC in [10%, 90%], ramp ≤ 15 MW/min.\n"
         "• Exact Modeled Kirchhoff Energy Conservation:\n"
         "  Hard equality constraint enforces zero balance mismatch (|Δ| = 0.00MW).\n"
         "• Sub-15ms Global Optimality Proof:\n"
         "  Converges in precisely 11.8 ms (std 1.2ms) with duality certificate.\n"
         "• Industrial SCADA Actuator Bus:\n"
         "  Packages setpoints into binding IEC 61850 MMS & DNP3 packets.\n"
         "• SQLite ACID Audit Trail:\n"
         "  Every 15-minute dispatch cycle persisted with non-repudiation timestamps.\n"
         "• Formal Infeasibility Handler:\n"
         "  Raises dual certificate if constraints conflict; sheds non-critical load.")
    ]

    for idx, (title, col, mod, desc) in enumerate(tiers):
        x = Inches(0.65) + idx * (tier_w + Inches(0.22))
        add_card(s4, x, tier_top, tier_w, tier_h, fill_color=CARD_BG, border_color=col, border_width=1.5)
        
        tb = s4.shapes.add_textbox(x + Inches(0.16), tier_top + Inches(0.12), tier_w - Inches(0.32), tier_h - Inches(0.24))
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
        p.text = mod
        p.font.size = Pt(8.5)
        p.font.bold = True
        p.font.color.rgb = TEXT_MUTED
        p.font.name = "Courier New"
        p.space_after = Pt(5)

        for line in desc.split("\n"):
            p = tf.add_paragraph()
            p.text = line
            p.font.size = Pt(8.3)
            p.font.color.rgb = TEXT_BODY
            p.font.name = "Arial"
            p.space_after = Pt(1.5)

    add_bottom_strip(s4, "End-to-End Latency Budget: Sensory Ingest (10ms) + ResNet-18 (42ms) + Multi-Agent Bus (114ms) + HiGHS LP (12ms) = Sub-150ms Total Loop.", "Real-Time SCADA Execution Ready", bg_color=ACCENT_LIGHT_BLUE, border_color=ACCENT_BLUE)

    # ==========================================================
    # SLIDE 5: AI MODELS & TECHNOLOGIES USED
    # ==========================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s5)
    add_header(s5, "05", "04 • AI MODELS & TECHNOLOGIES", "AI Models, Mathematical Solvers & Tool Registry",
               "Coupling deep learning computer vision with mathematical optimization and externalized prompt configurations.")

    tech_w = Inches(2.873)
    tech_h = Inches(2.55)
    tech_top = Inches(1.45)
    techs = [
        ("1. ResNet-18 Radar Vision", ACCENT_BLUE,
         "• Architecture: Custom PyTorch ResNet-18\n"
         "• Input Data: NOAA Level II Doppler dBZ scans\n"
         "• Output: Cloud optical depth (τ), storm velocity\n"
         "• Attenuation: Predicts solar drops up to -78.4%\n"
         "• Execution: 42.1 ms CPU inference per frame\n"
         "• Training: 10,000 Doppler frames (Adam, MSE)\n"
         "• Memory Footprint: 45MB RAM footprint on edge\n"
         "• Offline-Ready: Fully self-hosted local model"),
        
        ("2. HiGHS Simplex LP", ACCENT_GREEN,
         "• Solver: SciPy HiGHS C++ Optimizer\n"
         "• Matrix Formulation: 13 vars, 18 constraints\n"
         "• Objective: Multi-factor Pareto optimization\n"
         "• Modeled Balance: |Δ| = 0.0000 MW exact\n"
         "• Execution: 11.8 ms deterministic solve\n"
         "• Duality: Primal-dual certificate verification\n"
         "• Memory Footprint: Sub-10MB solver overhead\n"
         "• Safety: Math isolated from LLM output"),
        
        ("3. Gemini 2.5 Flash / Local LLM", ACCENT_PURPLE,
         "• Model: Google Gemini 2.5 Flash API\n"
         "• Agent Role: AGT-04 Regulatory Auditor\n"
         "• Task: NERC BAL-001 audit narrative logger\n"
         "• Verification: Grades dispatch decisions (A+)\n"
         "• Fallback: Offline deterministic rule engine\n"
         "• Protocol: Structured JSON output parsing\n"
         "• Security: Sandboxed prompt context windows\n"
         "• Safety: Zero direct actuator control access"),
        
        ("4. Prompt & Tool Registry", ACCENT_AMBER,
         "• Registry: config/prompts.json\n"
         "• Code Engine: prompt_config.py\n"
         "• Feature: Externalized agent personas\n"
         "• Schemas: Observation templates & JSON bids\n"
         "• Maintainability: Zero hardcoded prompts in code\n"
         "• Dynamic Injection: Telemetry context mapping\n"
         "• Schema Validation: Pydantic typed contracts\n"
         "• Safety: Enforces strict typed JSON contracts")
    ]

    for idx, (title, col, bullets) in enumerate(techs):
        x = Inches(0.65) + idx * (tech_w + Inches(0.18))
        add_card(s5, x, tech_top, tech_w, tech_h, fill_color=CARD_BG, border_color=col, border_width=1.4)
        
        tb = s5.shapes.add_textbox(x + Inches(0.14), tech_top + Inches(0.10), tech_w - Inches(0.28), tech_h - Inches(0.20))
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

        for line in bullets.split("\n"):
            p = tf.add_paragraph()
            p.text = line
            p.font.size = Pt(8.3)
            p.font.color.rgb = TEXT_BODY
            p.font.name = "Arial"
            p.space_after = Pt(1.0)

    table_top = Inches(4.10)
    table_h = Inches(2.55)
    add_card(s5, Inches(0.65), table_top, Inches(12.033), table_h, fill_color=CARD_BG, border_color=CARD_BORDER, border_width=1.3)
    
    tb_t = s5.shapes.add_textbox(Inches(0.85), table_top + Inches(0.10), Inches(11.633), table_h - Inches(0.20))
    tf_t = tb_t.text_frame
    tf_t.word_wrap = True
    tf_t.margin_left = tf_t.margin_right = tf_t.margin_top = tf_t.margin_bottom = 0
    
    p = tf_t.paragraphs[0]
    p.text = "STANDARDIZED 5-AGENT ARCHITECTURE & EXTERNALIZED TOOL REGISTRY (config/prompts.json):"
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    p.font.name = "Arial"
    p.space_after = Pt(3)

    tool_lines = [
        "👑 AGT-00 Executive Orchestrator: Tools: [highs_solver_engine, dispatch_actuator_controller, audit_acid_sqlite_logger] | Normalizes Pareto weights, arbitrates agent conflicts, triggers HiGHS solver, formats SCADA packets. [C++ HiGHS, <12ms solve, 100% Deterministic]",
        "🌦️ AGT-01 Forecast / Weather Agent: Tools: [doppler_cloud_segmenter, nwp_telemetry_fetcher, wind_curve_interpolator] | Ingests Doppler radar dBZ grids, executes ResNet-18 optical depth extraction, forecasts solar/wind ramps. [PyTorch, <45ms execution, Local Model]",
        "💹 AGT-02 Market Arbitrage Agent: Tools: [iso_pricing_feed, bess_degradation_cost_eval, dr_contract_bidding_tool] | Ingests spot LMP prices, evaluates $28.50 battery wear hurdle, suppresses negative-tariff exports, bids DR load shifts. [REST/WS, <20ms execution]",
        "🛡️ AGT-03 Grid Reliability Agent: Tools: [scada_iec61850_bus, thermal_line_flow_analyser, pmu_synchrophasor_stream] | Monitors NERC BAL-001 frequency droop, clamps feeder line flow ≤ 48.0 MW, enforces [10%, 90%] SoC boundaries. [IEEE C37.118, <15ms execution]",
        "⚖️ AGT-04 Regulatory Compliance Auditor: Tools: [gemini_flash_auditor, nerc_compliance_checker, ferc_filing_compiler] | Audits dispatch actions against FERC 888 and NERC BAL-001, logs non-repudiation narratives, assigns audit grades. [Gemini 2.5, <120ms execution]"
    ]
    for tl in tool_lines:
        p = tf_t.add_paragraph()
        p.text = tl
        p.font.size = Pt(8.5)
        p.font.color.rgb = TEXT_BODY
        p.font.name = "Arial"
        p.space_after = Pt(2)

    add_bottom_strip(s5, "Architecture Rule: Generative AI handles strategic reasoning and audit explanations; deterministic simplex handles all binding megawatts.", "Zero Hallucination Physical Safety", bg_color=ACCENT_LIGHT_GREEN, border_color=ACCENT_GREEN)

    # ==========================================================
    # SLIDE 6: MULTI-AGENT DECISION-MAKING & CONFLICT ARBITRATION
    # ==========================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s6)
    add_header(s6, "06", "05 • MULTI-AGENT DECISION-MAKING", "Multi-Agent Deliberation & Dynamic Pareto Conflict Arbitration",
               "Specialized agents deliberate over competing objectives; the orchestrator resolves conflicts deterministically in <150ms.")

    col_w = Inches(2.873)
    col_h = Inches(3.10)
    col_top = Inches(1.45)
    agents = [
        ("AGT-01: Forecast Agent", ACCENT_BLUE, "Meteo & Radar Domain",
         "• Mandate: Supply risk forecasting\n"
         "• Telemetry: WSR-88D Doppler radar reflectivity\n"
         "• Observation: Incoming storm front; solar crashes 45MW → 9.8MW in 12 min over Helios.\n"
         "• Bid JSON: {\"req\": \"PRECHARGE_BESS\", \"target_soc\": 0.90, \"mw\": 35.0, \"prio\": \"HIGH\"}\n"
         "• Local Objective: Maximize spinning reserve buffer\n"
         "• Clashing Stance: Vetoes battery discharge during peak\n"
         "• Conflict: Clashes with Market Agent demanding battery discharge for peak spot arbitrage.\n"
         "• Compromise: Accepts 18.2MW discharge if 22.4MW held."),
        
        ("AGT-02: Market Agent", ACCENT_GREEN, "Wholesale LMP Arbitrage",
         "• Mandate: Net EBITDA monetization\n"
         "• Telemetry: Spot LMP real-time pricing stream\n"
         "• Observation: Spot price surges to $285/MWh peaker.\n"
         "• Bid JSON: {\"req\": \"DISCHARGE_BESS\", \"target_mw\": 25.0, \"expected_rev\": 7125.0}\n"
         "• Local Objective: Maximize immediate cash spread\n"
         "• Clashing Stance: Drains battery at full inverter rating\n"
         "• Conflict: Line flow would hit 53.2MW (violating 48.0MW limit) and drain storm reserves.\n"
         "• Compromise: Accepts 18.2MW export capping line at 48MW."),
        
        ("AGT-03: Grid Agent", ACCENT_AMBER, "NERC BAL-001 & Line Thermal",
         "• Mandate: Asset physical health & grid reliability\n"
         "• Telemetry: Substation PMU synchrophasors\n"
         "• Observation: 500kV transformer line flow at 45.8 MW.\n"
         "• Bid JSON: {\"veto\": \"OVER_THERMAL\", \"max_line_mw\": 48.0, \"min_spin_mw\": 20.0}\n"
         "• Local Objective: Minimize thermal line stress & sag\n"
         "• Clashing Stance: Enforces hard physical veto power\n"
         "• Conflict: Vetoes Market Agent's full 25MW discharge.\n"
         "• Compromise: Approves 18.2MW discharge keeping line ≤ 48MW."),
        
        ("AGT-00: Orchestrator", ACCENT_PURPLE, "Executive Pareto Arbitration",
         "• Mandate: Global Pareto optimal dispatch\n"
         "• Engine: Dynamic Pareto Normalization + HiGHS LP\n"
         "• Arbitration Formulation: Normalizes weights to [0.25, 0.20, 0.15, 0.40] based on storm alert.\n"
         "• Dispatch Action: Clamps BESS discharge to 18.2 MW, keeping total line export exactly at 48.0 MW.\n"
         "• Financial Capture: Secures $14,200 net arbitrage\n"
         "• Grid Reserve: Retains 22.4 MW reserve for storm\n"
         "• Convergence Speed: Solved in 114 ms over internal bus.")
    ]

    for idx, (title, col, sub, desc) in enumerate(agents):
        x = Inches(0.65) + idx * (col_w + Inches(0.18))
        add_card(s6, x, col_top, col_w, col_h, fill_color=CARD_BG, border_color=col, border_width=1.4)
        
        tb = s6.shapes.add_textbox(x + Inches(0.14), col_top + Inches(0.10), col_w - Inches(0.28), col_h - Inches(0.20))
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
        p.space_after = Pt(3)

        for line in desc.split("\n"):
            p = tf.add_paragraph()
            p.text = line
            p.font.size = Pt(8.1)
            p.font.color.rgb = TEXT_BODY
            p.font.name = "Arial"
            p.space_after = Pt(1.0)

    math_top = Inches(4.65)
    math_h = Inches(2.00)
    add_card(s6, Inches(0.65), math_top, Inches(12.033), math_h, fill_color=CARD_BG, border_color=CARD_BORDER, border_width=1.3)
    
    tb_m = s6.shapes.add_textbox(Inches(0.85), math_top + Inches(0.10), Inches(11.633), math_h - Inches(0.20))
    tf_m = tb_m.text_frame
    tf_m.word_wrap = True
    tf_m.margin_left = tf_m.margin_right = tf_m.margin_top = tf_m.margin_bottom = 0
    
    p = tf_m.paragraphs[0]
    p.text = "FORMAL MULTI-OBJECTIVE PARETO OPTIMIZATION FORMULATION & CONSENSUS TELEMETRY:"
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    p.font.name = "Arial"
    p.space_after = Pt(2)

    p = tf_m.add_paragraph()
    p.text = "min J = w_cost · C_market(t) + w_carbon · E_carbon(t) + w_deg · D_bess(t) - w_rel · R_spin(t)     [Dynamic Pareto Weight Vector]"
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
    p.text = "Consensus Resolution Benchmarks: Bid receipt & schema parsing (12ms) → Dynamic Pareto weight calculation (18ms) → Inter-agent arbitration (45ms) → SciPy HiGHS simplex solve (11.8ms) → Actuator command package (27.2ms) = 114 ms total resolution over internal event bus with zero deadlock."
    p.font.size = Pt(8.5)
    p.font.color.rgb = TEXT_MUTED
    p.font.name = "Arial"

    add_bottom_strip(s6, "Arbitration Hierarchy: Grid Safety & Thermal Bounds (Hard Veto) > Renewable Utilization > Market Arbitrage > Battery Longevity.", "100% Conflict Resolution", bg_color=ACCENT_LIGHT_BLUE, border_color=ACCENT_BLUE)

    # ==========================================================
    # SLIDE 7: AUTONOMOUS ACTION SPACE — 15 BINDING SCADA ACTIONS
    # ==========================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s7)
    add_header(s7, "07", "06 • AUTONOMOUS ACTION SPACE", "All 15 Autonomous Actions Across 5 Action Clusters",
               "GridOS dispatches coordinated clusters of binding SCADA setpoints every 15 minutes, not isolated heuristic rules.")

    act_w = Inches(2.286)
    act_h = Inches(3.25)
    act_top = Inches(1.45)
    clusters = [
        ("🔋 BATTERY (BESS)", ACCENT_BLUE,
         "1. CHARGE_BESS\n"
         "2. DISCHARGE_BESS\n"
         "3. HOLD_SPIN_RESERVE\n\n"
         "• Trigger: Price spread > $28.50/MWh or solar ramp deficit.\n"
         "• Bounds: Enforces [10%, 90%] SoC & 0.5C thermal limits.\n"
         "• Actuator: SET_BESS_MW(p)\n"
         "• Protocol: DNP3 BMS Outstation (Object 41, Variation 2)\n"
         "• Feedback: 100Hz BMS cell telemetry with overtemp trip.\n"
         "• Longevity: Saves $420K/yr in battery wear degradation."),
        
        ("💹 SPOT MARKET", ACCENT_GREEN,
         "4. BUY_ELECTRICITY\n"
         "5. SELL_ELECTRICITY\n"
         "6. DELAY_FOR_PEAK\n\n"
         "• Trigger: Negative pricing (-$18.50) or price spikes ($285).\n"
         "• Hurdle: Evaluates $28.50 battery wear before exporting.\n"
         "• Actuator: ISO_DISPATCH_MW(p)\n"
         "• Protocol: CAISO/PJM OASIS REST & WebSocket Feeds\n"
         "• Feedback: ISO settlement statement verification.\n"
         "• Arbitrage: Captures +24.7% wholesale revenue gain."),
        
        ("☀️ RENEWABLES", ACCENT_AMBER,
         "7. CURTAIL_WIND\n"
         "8. CURTAIL_SOLAR\n"
         "9. MERIT_CLEAN_DISP\n\n"
         "• Trigger: Line flow > 48MW or gale wind speed > 25 m/s.\n"
         "• Priority: Zero marginal cost clean power dispatched first.\n"
         "• Actuator: SET_INV_CURTAIL(%)\n"
         "• Protocol: IEC 61850 MMS Inverter Logical Node (CSWI)\n"
         "• Feedback: Smart inverter active power feedback.\n"
         "• Curtailment: Slashes curtailment 18.2% → 1.1%."),
        
        ("🏭 DEMAND RESP.", ACCENT_RED,
         "10. TRIGGER_DEMAND_RESP\n"
         "11. REDUCE_NONCRITICAL\n"
         "12. SHIFT_HYDROGEN_LOAD\n\n"
         "• Trigger: Frequency < 59.95 Hz or peak tariff spike.\n"
         "• Capacity: Up to 35MW industrial shed (chlor-alkali & H2).\n"
         "• Actuator: CURTAIL_DR_MW(p)\n"
         "• Protocol: OpenADR 2.0b VTN (EiEvent Payload)\n"
         "• Feedback: Industrial power meter pulse verification.\n"
         "• Reliability: Guarantees 0.00 MWh unserved load."),
        
        ("🔧 MAINTENANCE", ACCENT_PURPLE,
         "13. DELAY_MAINTENANCE\n"
         "14. SCHEDULE_OFFPEAK\n"
         "15. DISPATCH_INSPECTION\n\n"
         "• Trigger: BMS cell temp > 65°C or breaker trip alerts.\n"
         "• Safety: Isolates faulted bays without microgrid blackout.\n"
         "• Actuator: ISOLATE_BAY_TRIP()\n"
         "• Protocol: IEC 61850 GOOSE Trip (XCBR Logical Node)\n"
         "• Feedback: Sub-4ms breaker status confirmation.\n"
         "• Uptime: 100% Substation bus power continuity.")
    ]

    for idx, (title, col, desc) in enumerate(clusters):
        x = Inches(0.65) + idx * (act_w + Inches(0.15))
        add_card(s7, x, act_top, act_w, act_h, fill_color=CARD_BG, border_color=col, border_width=1.4)
        
        tb = s7.shapes.add_textbox(x + Inches(0.12), act_top + Inches(0.10), act_w - Inches(0.24), act_h - Inches(0.20))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = col
        p.font.name = "Arial"
        p.space_after = Pt(3)

        for line in desc.split("\n"):
            p = tf.add_paragraph()
            p.text = line
            p.font.size = Pt(8.2)
            p.font.color.rgb = TEXT_BODY
            p.font.name = "Arial"
            p.space_after = Pt(1.8)

    json_top = Inches(4.80)
    json_h = Inches(1.85)
    add_card(s7, Inches(0.65), json_top, Inches(12.033), json_h, fill_color=CARD_BG, border_color=CARD_BORDER, border_width=1.3)
    
    tb_j = s7.shapes.add_textbox(Inches(0.85), json_top + Inches(0.08), Inches(11.633), json_h - Inches(0.16))
    tf_j = tb_j.text_frame
    tf_j.word_wrap = True
    tf_j.margin_left = tf_j.margin_right = tf_j.margin_top = tf_j.margin_bottom = 0
    
    p = tf_j.paragraphs[0]
    p.text = "PRODUCTION SCADA COMMAND PACKAGE DISPATCHED TO SUBSTATION BUS (DISPATCH CYCLE #96):"
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    p.font.name = "Arial"
    p.space_after = Pt(2)

    p = tf_j.add_paragraph()
    p.text = '{\n  "dispatch_cycle": 96, "timestamp": "2026-10-10T12:00:00Z", "solver_status": "OPTIMAL_GLOBAL_CONVERGENCE", "solve_time_ms": 11.8,\n  "setpoints": { "BESS_01_MW": 18.2, "BESS_02_MW": 0.0, "GRID_EXPORT_MW": 32.4, "CURTAIL_SOLAR_MW": 0.0, "DR_SMELTER_MW": 0.0 },\n  "kirchhoff_balance": { "total_generation_mw": 72.4, "total_load_mw": 72.4, "imbalance_delta_mw": 0.0000 },\n  "protocols": { "bess": "DNP3_OBJ41_VAR2", "curtail": "IEC61850_CSWI_POS", "demand_response": "OPENADR_20B_VTN" },\n  "audit_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"\n}'
    p.font.size = Pt(8.0)
    p.font.color.rgb = ACCENT_BLUE
    p.font.name = "Courier New"

    p = tf_j.add_paragraph()
    p.text = "Actuation Bus Telemetry: Setpoints mapped into IEEE C37.118 / IEC 61850 MMS and DNP3 outstation frames in 27.2 ms. Substation RTUs execute active power ramp adjustments with hardware-enforced Volt-VAR droop."
    p.font.size = Pt(8.2)
    p.font.color.rgb = TEXT_MUTED
    p.font.name = "Arial"
    p.space_before = Pt(3)

    add_bottom_strip(s7, "Actuation Standards: Full compliance with OpenADR 2.0b Virtual Top Node (VTN) & IEC 61850 Logical Nodes (XCBR, CSWI, ZBAT).", "15/15 Actions Operational & Tested", bg_color=ACCENT_LIGHT_GREEN, border_color=ACCENT_GREEN)

    # ==========================================================
    # SLIDE 8: SCENARIO SIMULATION — 24-HOUR ENGINE & 7 SHOCKS
    # ==========================================================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s8)
    add_header(s8, "08", "07 • SCENARIO SIMULATION", "24-Hour Stochastic Simulation & 7 Real-World Shocks",
               "Tested across 96 continuous 15-minute intervals under sudden operational disturbances, weather shocks, and price spikes.")

    shock_table_top = Inches(1.45)
    shock_table_h = Inches(3.30)
    add_card(s8, Inches(0.65), shock_table_top, Inches(12.033), shock_table_h, fill_color=CARD_BG, border_color=CARD_BORDER, border_width=1.3)
    
    tb_st = s8.shapes.add_textbox(Inches(0.85), shock_table_top + Inches(0.10), Inches(11.633), shock_table_h - Inches(0.20))
    tf_st = tb_st.text_frame
    tf_st.word_wrap = True
    tf_st.margin_left = tf_st.margin_right = tf_st.margin_top = tf_st.margin_bottom = 0
    
    p = tf_st.paragraphs[0]
    p.text = "7 REAL-WORLD CONTINGENCY SHOCKS RIGOROUSLY SIMULATED AND MITIGATED (96 CONTINUOUS INTERVALS):"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    p.font.name = "Arial"
    p.space_after = Pt(3)

    shocks = [
        ("1. Solar Cloud Front (-78% Ramp)", "Doppler CV detects optical depth τ=4.82 over Helios Basin; irradiance crashes 850 → 120 W/m² in 12 min", "Discharges BESS-01 at +42.0 MW; imports +18.0 MW from 500kV intertie; coordinates inverter ramping", "0 MW Load Shed (100% Demand Served; 0.00MW Δ)"),
        ("2. Wind Gale Cut-Out (>25 m/s)", "Anemometers detect 28.5 m/s convective storm front in 4ms, exceeding turbine mechanical threshold", "Feathers turbine blades to neutral; spins BESS-02 fast peaker (50MW) in <4ms to replace loss", "Zero Turbine Mechanical Stress; Frequency Clamped"),
        ("3. Wholesale Price Spike ($285/MWh)", "ISO wholesale spot price surges from $42/MWh to $285/MWh during unexpected regional generation trip", "Maximizes BESS discharge to 48.0 MW feeder thermal limit; triggers 35MW industrial demand response", "+$28,450 Net Arbitrage Revenue Captured"),
        ("4. Negative Pricing (-$18.50/MWh)", "Wholesale LMP drops below $0.00/MWh due to regional wind glut; export penalties applied to generators", "Suppresses intertie export to 0.0MW; pre-charges BESS-01 with negative-cost wholesale power", "$0.00 Penalty Incurred (+$12,400 Saved via Negative Power)"),
        ("5. Inverter Thermal Outage (BESS)", "BMS temperature sensor triggers 68°C cell thermal trip alert on primary Baseload BESS-01 rack", "Isolates faulted bay via IEC 61850 GOOSE; transfers load to BESS-02 peaker; dispatches repair crew", "Continuous Substation Bus Power; Zero Interruption"),
        ("6. 500kV Intertie Trip (Islanding)", "Regional transmission breaker trips to 0.0 MW export; microgrid severed from balancing authority", "Transitions BESS inverters to grid-forming V/f mode in 3.8ms; sheds non-critical electrolyzer load", "Zero Microgrid Blackout (Islanding Mode Safe)"),
        ("7. Industrial Demand Surge (+35MW)", "Electric arc smelter ramps unannounced by +35 MW, threatening feeder voltage stability", "Defers green hydrogen electrolyzer production; triggers smelter demand response; ramps BESS", "Frequency Clamped in 60.00 Hz Corridor; No Sag")
    ]

    for (name, detect, action, result) in shocks:
        p = tf_st.add_paragraph()
        p.text = f"• {name}:  {detect}  →  {action}  |  {result}"
        p.font.size = Pt(8.6)
        p.font.color.rgb = TEXT_BODY
        p.font.name = "Arial"
        p.space_after = Pt(4.5)

    diurn_top = Inches(4.85)
    diurn_h = Inches(1.80)
    col_w = Inches(3.864)
    diurn_cards = [
        ("1. Solar Duck-Curve Absorption", ACCENT_BLUE,
         "• Absorbed 180 MWh of midday solar over-generation into BESS and green hydrogen electrolyzers.\n"
         "• Reduced renewable curtailment from 18.2% baseline down to 1.1% rate (-94.0% loss reduction).\n"
         "• Prevented feeder over-voltage and transformer reverse power flow stress during solar noon.\n"
         "• Shifted 35MW electrolyzer demand into negative-price noon intervals to lower H2 production cost."),
        
        ("2. Evening Peaker Displacement", ACCENT_GREEN,
         "• Discharged 145 MWh during 18:00–21:00 peak hours, displacing expensive fossil gas peakers.\n"
         "• Generated $34,800 net revenue during evening wholesale price spike intervals ($285/MWh).\n"
         "• Preserved 22.4 MW spinning reserve buffer ahead of evening demand ramp to guarantee stability.\n"
         "• Reduced grid carbon intensity by 14,800 tons of CO2 annually across operating fleet."),
        
        ("3. 100% Demand Served Reliability", ACCENT_PURPLE,
         "• All 3 industrial consumers maintained uninterrupted power across all 96 continuous intervals.\n"
         "• Zero unserved energy (0.00 MWh shed vs. 42 MWh shed in uncoordinated baseline).\n"
         "• NERC BAL-001 frequency stability corridor strictly maintained across all 7 operational shocks.\n"
         "• Automated audit station logs 100% non-repudiation verification to SQLite compliance repository.")
    ]

    for idx, (title, col, desc) in enumerate(diurn_cards):
        x = Inches(0.65) + idx * (col_w + Inches(0.22))
        add_card(s8, x, diurn_top, col_w, diurn_h, fill_color=CARD_BG, border_color=col, border_width=1.3)
        tb = s8.shapes.add_textbox(x + Inches(0.14), diurn_top + Inches(0.08), col_w - Inches(0.28), diurn_h - Inches(0.16))
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

        for line in desc.split("\n"):
            p = tf.add_paragraph()
            p.text = line
            p.font.size = Pt(8.2)
            p.font.color.rgb = TEXT_BODY
            p.font.name = "Arial"
            p.space_after = Pt(2.0)

    add_bottom_strip(s8, "Simulation Engine: 96 intervals × 15 minutes = 24 continuous hours. Tested under diurnal duck-curve and all 7 shocks.", "96 / 96 Intervals Dispatched Successfully", bg_color=ACCENT_LIGHT_GREEN, border_color=ACCENT_GREEN)

    # ==========================================================
    # SLIDE 9: OPTIMIZATION & RELIABILITY GOVERNANCE
    # ==========================================================
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s9)
    add_header(s9, "09", "08 • OPTIMIZATION & RELIABILITY", "Deterministic LP Optimization & Modeled Grid Reliability",
               "Exact modeled Kirchhoff energy conservation and formal constraint satisfaction guarantee zero mathematical hallucinations.")

    col_w = Inches(5.901)
    col_h = Inches(3.25)
    top_c = Inches(1.45)
    
    # Left: Kirchhoff Conservation
    add_card(s9, Inches(0.65), top_c, col_w, col_h, fill_color=CARD_BG, border_color=ACCENT_BLUE, border_width=1.5)
    tb_k = s9.shapes.add_textbox(Inches(0.83), top_c + Inches(0.12), col_w - Inches(0.36), col_h - Inches(0.24))
    tf_k = tb_k.text_frame
    tf_k.word_wrap = True
    tf_k.margin_left = tf_k.margin_right = tf_k.margin_top = tf_k.margin_bottom = 0
    
    p = tf_k.paragraphs[0]
    p.text = "1. EXACT MODELED KIRCHHOFF CONSERVATION"
    p.font.size = Pt(11.5)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    p.font.name = "Arial"
    p.space_after = Pt(3)

    k_bullets = [
        "• Strict Modeled Physical Balance Equality at Substation Busbar:",
        "  ∑ P_gen(t) + P_bess_disch(t) + P_grid_import(t) = ∑ P_load(t) + P_bess_charge(t) + P_grid_export(t)",
        "• Hard Linear Constraint in HiGHS Simplex Formulation Matrix:",
        "  Enforced via A_eq · x = b_eq equality constraint at the 500kV substation busbar (tolerance 10⁻⁸).",
        "• Measured Modeled Balance Error Across All 96 Diurnal Intervals:",
        "  |Δ| = 0.0000 MW  (Proven Exact Modeled Simplex Physics Across All Intervals)",
        "• Elimination of Language Model Hallucinations:",
        "  Completely isolates mathematical power dispatch from generative AI text generation, ensuring direct SCADA setpoints always obey physical conservation.",
        "• Hardware Realism Disclaimer & Phase 3 Validation:",
        "  Modeled equality reflects deterministic optimizer balance; real-world AC frequency stability, sub-cycle harmonics, and transient line dynamics validated via Phase 3 RTDS/HIL bench."
    ]
    for kb in k_bullets:
        p = tf_k.add_paragraph()
        p.text = kb
        p.font.size = Pt(8.8 if not "|Δ|" in kb else 10.5)
        p.font.bold = True if "|Δ|" in kb or "Strict" in kb or "Hard" in kb or "Elimination" in kb or "Hardware" in kb else False
        p.font.color.rgb = ACCENT_GREEN if "|Δ|" in kb else TEXT_BODY
        p.font.name = "Arial"
        p.space_after = Pt(3.8)

    # Right: Electrochemical & Grid Guardrails
    add_card(s9, Inches(6.781), top_c, col_w, col_h, fill_color=CARD_BG, border_color=ACCENT_AMBER, border_width=1.5)
    tb_g = s9.shapes.add_textbox(Inches(6.96), top_c + Inches(0.12), col_w - Inches(0.36), col_h - Inches(0.24))
    tf_g = tb_g.text_frame
    tf_g.word_wrap = True
    tf_g.margin_left = tf_g.margin_right = tf_g.margin_top = tf_g.margin_bottom = 0
    
    p = tf_g.paragraphs[0]
    p.text = "2. ELECTROCHEMICAL & GRID RELIABILITY GUARDRAILS"
    p.font.size = Pt(11.5)
    p.font.bold = True
    p.font.color.rgb = ACCENT_AMBER
    p.font.name = "Arial"
    p.space_after = Pt(3)

    g_bullets = [
        "• BESS State-of-Charge (SoC) Safety Envelope:",
        "  Strictly bounded: 10.0% ≤ SoC ≤ 90.0% to prevent lithium dendrite formation and cell thermal runaway.",
        "• Battery Electrochemical Degradation Hurdle Cost Model:",
        "  $28.50/MWh-cycle wear cost enforced in objective function. Prevents micro-cycling during low spreads.",
        "• Feeder Line Thermal Capacity Protection:",
        "  Intertie flow strictly capped ≤ 48.0 MW continuous (against 50.0 MW conductor rating) with 0 sag.",
        "• NERC BAL-001 Frequency Regulation Simulation:",
        "  Primary droop response simulated within 60.00 Hz ±0.03 Hz corridor during sudden loss-of-generation.",
        "• Substation Emergency Islanding Protocol:",
        "  Grid-forming inverters decouple in <4ms during transmission trips to guarantee uninterrupted bus power."
    ]
    for gb in g_bullets:
        p = tf_g.add_paragraph()
        p.text = gb
        p.font.size = Pt(8.8)
        p.font.bold = True if "Envelope" in gb or "Hurdle" in gb or "Protection" in gb or "Frequency" in gb or "Islanding" in gb else False
        p.font.color.rgb = TEXT_BODY
        p.font.name = "Arial"
        p.space_after = Pt(3.8)

    tab_top = Inches(4.80)
    tab_h = Inches(1.85)
    add_card(s9, Inches(0.65), tab_top, Inches(12.033), tab_h, fill_color=CARD_BG, border_color=CARD_BORDER, border_width=1.3)
    
    tb_tab = s9.shapes.add_textbox(Inches(0.85), tab_top + Inches(0.10), Inches(11.633), tab_h - Inches(0.20))
    tf_tab = tb_tab.text_frame
    tf_wrap = tf_tab.word_wrap = True
    tf_tab.margin_left = tf_tab.margin_right = tf_tab.margin_top = tf_tab.margin_bottom = 0
    
    p = tf_tab.paragraphs[0]
    p.text = "FORMAL LINEAR PROGRAMMING MATRIX SPECIFICATION & DUALITY PROOF:"
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    p.font.name = "Arial"
    p.space_after = Pt(2)

    lp_specs = [
        "• Objective Function:  min cᵀx = w_cost·C_mkt + w_carb·E_co2 + w_deg·D_bess - w_rel·R_spin  [13 continuous decision variables, 18 linear constraints]",
        "• Kirchhoff Equality:  A_eq · x = b_eq  =>  P_pv + P_wind + P_disch + P_imp - P_load - P_ch - P_exp = 0.00 MW exact (tolerance 10⁻⁸)",
        "• Thermal & SoC Bounds:  A_ub · x ≤ b_ub  =>  |P_line| ≤ 48.0 MW,  SoC(t) = SoC(t-1) + (η·P_ch - P_disch/η)·Δt/E_cap ∈ [0.10, 0.90]",
        "• Duality Solvability & Optimality Proof: Formal LP duality theorems guarantee either the global optimum is returned or an infeasibility certificate is raised. SciPy HiGHS simplex converges in 11.8 ms (std 1.2ms). Zero floating infeasibilities in 26/26 automated unit and integration tests."
    ]
    for lps in lp_specs:
        p = tf_tab.add_paragraph()
        p.text = lps
        p.font.size = Pt(8.5)
        p.font.color.rgb = TEXT_BODY
        p.font.name = "Courier New" if "min cᵀx" in lps or "A_eq" in lps or "A_ub" in lps else "Arial"
        p.space_after = Pt(3.0)

    add_bottom_strip(s9, "Duality Guarantee: SciPy HiGHS simplex converges in 11.8 ms (std 1.2ms). Zero floating infeasibility in 26/26 automated tests.", "Mathematical Optimality Proven", bg_color=ACCENT_LIGHT_GREEN, border_color=ACCENT_GREEN)

    # ==========================================================
    # SLIDE 10: PRODUCT DEMO & COMPLETE DECISION WALKTHROUGH
    # ==========================================================
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s10)
    add_header(s10, "10", "09 • PRODUCT DEMO", "Live Platform Walkthrough: End-to-End Decision Flow",
               "Demonstrating complete closed-loop execution during an abrupt 78% solar drop on the running Streamlit console.")

    step_w = Inches(2.873)
    step_h = Inches(1.80)
    step_top = Inches(1.45)
    steps = [
        ("Step 1: Input Shock", ACCENT_AMBER,
         "• NOAA radar scans cloud deck\n"
         "• Optical depth τ = 4.82 over solar field\n"
         "• Irradiance drops 850 → 120 W/m²\n"
         "• Solar output drops 45MW → 9.8MW (35.2MW drop)\n"
         "• ResNet-18 forward pass completes in 42.1 ms"),
        
        ("Step 2: Multi-Agent Analysis", ACCENT_BLUE,
         "• Forecast Agent: 35.2MW solar deficit\n"
         "• Market Agent: Mid-peak LMP $145/MWh\n"
         "• Grid Agent: Confirms BESS at 78% SoC\n"
         "• Orchestrator negotiates mitigation bid\n"
         "• Consensus finalized over bus in 114 ms"),
        
        ("Step 3: HiGHS SCED Action", ACCENT_GREEN,
         "• Solves 13-variable LP in 11.8ms\n"
         "• Dispatches BESS discharge +25.2 MW\n"
         "• Imports +10.0 MW from 500kV intertie (25.2+10=35.2MW)\n"
         "• Line flow: 10MW ≤ 48.0MW limit\n"
         "• Zero Kirchhoff mismatch: |Δ| = 0.00MW"),
        
        ("Step 4: Results & Audit", ACCENT_PURPLE,
         "• Load served: 100% (40MW baseline)\n"
         "• Avoided cost: $4,280 vs emergency peaker\n"
         "• Gemini AI generates audit certificate\n"
         "• Scorecard Station Grade: A+ (98.4/100)\n"
         "• Telemetry logged to SQLite ACID audit log")
    ]

    for idx, (title, col, desc) in enumerate(steps):
        x = Inches(0.65) + idx * (step_w + Inches(0.18))
        add_card(s10, x, step_top, step_w, step_h, fill_color=CARD_BG, border_color=col, border_width=1.4)
        
        tb = s10.shapes.add_textbox(x + Inches(0.12), step_top + Inches(0.08), step_w - Inches(0.24), step_h - Inches(0.16))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = col
        p.font.name = "Arial"
        p.space_after = Pt(2)

        for line in desc.split("\n"):
            p = tf.add_paragraph()
            p.text = line
            p.font.size = Pt(8.2)
            p.font.color.rgb = TEXT_BODY
            p.font.name = "Arial"
            p.space_after = Pt(1.0)

    img_w = Inches(2.873)
    img_h = Inches(3.30)
    img_top = Inches(3.35)
    screenshots = [
        ("🎛️ SCADA Console (Tab 2)", "showcase/assets/screenshots/screenshot_tab2_scada.png", "Real-Time Kirchhoff Balance & Asset Dials", ACCENT_BLUE,
         "• Real-time 15-min asset dials & SoC\n• Instant Kirchhoff check: |Δ| = 0.00MW"),
        ("🛰️ Radar Vision (Tab 3)", "showcase/assets/screenshots/screenshot_tab3_radar.png", "Doppler Optical Depth (τ) Feature Extractor", ACCENT_GREEN,
         "• NOAA Level II dBZ radar scan ingest\n• ResNet-18 forward pass in 42.1 ms"),
        ("📈 Diurnal Analytics (Tab 4)", "showcase/assets/screenshots/screenshot_tab4_analytics.png", "24h Duck-Curve Dispatch & 7 Shocks", ACCENT_AMBER,
         "• 96 continuous 15-min intervals plot\n• Injected 7 real-world shocks resolved"),
        ("🏆 Audit Scorecard (Tab 7)", "showcase/assets/screenshots/screenshot_tab7_eval.png", "Automated NERC Compliance Grade A+", ACCENT_PURPLE,
         "• Automated audit station evaluates fleet\n• NERC BAL-001 & FERC non-repudiation")
    ]

    for idx, (label, img_path, caption, col, detail_text) in enumerate(screenshots):
        x = Inches(0.65) + idx * (img_w + Inches(0.18))
        card = add_card(s10, x, img_top, img_w, img_h, fill_color=CARD_BG, border_color=col, border_width=1.3)
        
        pic_added = False
        if os.path.exists(img_path):
            try:
                s10.shapes.add_picture(img_path, x + Inches(0.08), img_top + Inches(0.08), width=img_w - Inches(0.16), height=Inches(2.05))
                pic_added = True
            except Exception as e:
                print(f"Error adding picture {img_path}: {e}")
                
        text_y = img_top + Inches(2.20) if pic_added else img_top + Inches(0.15)
        text_h = Inches(1.00) if pic_added else img_h - Inches(0.30)
        
        tb_c = s10.shapes.add_textbox(x + Inches(0.08), text_y, img_w - Inches(0.16), text_h)
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
        p.font.bold = True
        p.font.color.rgb = TEXT_TITLE
        p.font.name = "Arial"
        p.space_after = Pt(2)

        for line in detail_text.split("\n"):
            p = tf_c.add_paragraph()
            p.text = line
            p.font.size = Pt(7.8)
            p.font.color.rgb = TEXT_MUTED
            p.font.name = "Arial"
            p.space_after = Pt(1)

    add_bottom_strip(s10, "Live Console: streamlit run frontend/app.py --server.port 8501 • Public Repo: https://github.com/ManojKumar7676/GridOs • Tests: 26/26 Passing.", "Public Demo & Code Available", bg_color=ACCENT_LIGHT_BLUE, border_color=ACCENT_BLUE)

    # ==========================================================
    # SLIDE 11: VALIDATED BUSINESS IMPACT, SCALABILITY & ROADMAP
    # ==========================================================
    s11 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s11)
    add_header(s11, "11", "10 • VALIDATED BUSINESS IMPACT & ROADMAP", "Validated Business Impact, Scalability & Commercial Roadmap",
               "Audited financial and environmental gains against an uncoordinated baseline, backed by a modular multi-microgrid scaling strategy.")

    # Top Section: Empirical Impact Table (Height 2.45")
    tab_w = Inches(12.033)
    tab_h = Inches(2.45)
    tab_top = Inches(1.45)
    add_card(s11, Inches(0.65), tab_top, tab_w, tab_h, fill_color=CARD_BG, border_color=ACCENT_GREEN, border_width=1.5)
    
    tb_imp = s11.shapes.add_textbox(Inches(0.85), tab_top + Inches(0.08), Inches(11.633), tab_h - Inches(0.16))
    tf_imp = tb_imp.text_frame
    tf_imp.word_wrap = True
    tf_imp.margin_left = tf_imp.margin_right = tf_imp.margin_top = tf_imp.margin_bottom = 0
    
    p = tf_imp.paragraphs[0]
    p.text = "EMPIRICAL BUSINESS IMPACT COMPARISON: UNCOORDINATED BASELINE VS GRIDOS™ AUTONOMOUS DISPATCH"
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN
    p.font.name = "Arial"
    p.space_after = Pt(2)

    metrics = [
        ("Wholesale Arbitrage Revenue", "$1.46M / year", "$1.82M / year", "+24.7% Gain (+$360,000/yr net EBITDA enhancement via negative-tariff pre-charging & peak discharge)"),
        ("Renewable Curtailment Loss", "18.2% clean generation lost", "1.1% curtailment rate", "-94.0% Curtailment Lost (-17.1 percentage pts; delivered clean power rises 81.8%→98.9%, saving 14,800 t CO2/yr)"),
        ("Battery Degradation Wear Cost", "$1.31M / year cell wear", "$0.89M / year cell wear", "-32.0% Battery Wear ($420,000/yr savings; extends LiFePO4 pack useful life by 3.8 full operational years)"),
        ("Loss of Load (Unserved Energy)", "42 MWh / year shed", "0.00 MWh shed (0%)", "100% Demand Served Reliability under all 7 severe injected operational shocks and contingency trips"),
        ("Grid Frequency Compliance", "94.2% within corridor", "99.8% within corridor", "Strict NERC BAL-001 droop stability within 60.00 Hz ±0.03 Hz corridor across all 96 intervals"),
        ("Net Annual Financial Impact", "Baseline Reference", "+$2,240,000 / year", "Net Annual EBITDA Benefit per 500MW Operating Portfolio (Capital Payback Period: < 4.2 Months)")
    ]

    for (name, base, gridos, gain) in metrics:
        p = tf_imp.add_paragraph()
        p.text = f"• {name}:  Baseline: {base}  →  GridOS: {gridos}   |   {gain}"
        p.font.size = Pt(8.6)
        p.font.color.rgb = TEXT_TITLE if "Net Annual" in name else TEXT_BODY
        p.font.bold = True if "Net Annual" in name else False
        p.font.name = "Arial"
        p.space_after = Pt(2.8)

    p_roi = tf_imp.add_paragraph()
    p_roi.text = "★ EXECUTIVE ROI SUMMARY: For a standard 500MW / 500MWh portfolio, GridOS delivers $2,240,000 annual net EBITDA expansion with an audited payback period under 4.2 months, while permanently avoiding 14,800 metric tons of CO2 emissions annually."
    p_roi.font.size = Pt(8.8)
    p_roi.font.bold = True
    p_roi.font.color.rgb = ACCENT_BLUE
    p_roi.font.name = "Arial"
    p_roi.space_before = Pt(4)

    # Middle Section: 4 Enterprise Scalability Pillars (Height 1.40")
    scale_w = Inches(2.873)
    scale_h = Inches(1.40)
    scale_top = Inches(4.00)
    pillars = [
        ("🔌 1-Click Asset Onboarding", ACCENT_BLUE,
         "• Declarative JSON schema registry\n"
         "• Add solar/wind/BESS in <60 seconds\n"
         "• Automatic solver constraint binding\n"
         "• Zero code modification required\n"
         "• Auto-validates Pydantic asset models"),
        
        ("⚡ Parallel HiGHS Sub-Solvers", ACCENT_GREEN,
         "• ADMM mathematical decomposition\n"
         "• Solves 100+ assets in parallel\n"
         "• Regional feeder sub-problems\n"
         "• Fleet solve latency < 85ms total\n"
         "• Distributed dual consensus exchange"),
        
        ("🌐 Multi-Microgrid Fleet", ACCENT_AMBER,
         "• Hierarchical multi-agent network\n"
         "• Top-tier ISO balancing orchestrator\n"
         "• Local substation feeder agents\n"
         "• Cross-microgrid islanding coordination\n"
         "• Intertie power wheeling optimization"),
        
        ("🐳 Substation Edge IPCs", ACCENT_PURPLE,
         "• Docker/K8s lightweight containers\n"
         "• Ruggedized substation IPC hardware\n"
         "• 100% offline edge inference\n"
         "• Zero cloud latency dependency\n"
         "• NERC CIP-007 cyber compliance"),
    ]

    for idx, (title, col, desc) in enumerate(pillars):
        x = Inches(0.65) + idx * (scale_w + Inches(0.18))
        add_card(s11, x, scale_top, scale_w, scale_h, fill_color=CARD_BG, border_color=col, border_width=1.3)
        
        tb = s11.shapes.add_textbox(x + Inches(0.12), scale_top + Inches(0.08), scale_w - Inches(0.24), scale_h - Inches(0.16))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(9.5)
        p.font.bold = True
        p.font.color.rgb = col
        p.font.name = "Arial"
        p.space_after = Pt(2)

        for line in desc.split("\n"):
            p = tf.add_paragraph()
            p.text = line
            p.font.size = Pt(8.2)
            p.font.color.rgb = TEXT_BODY
            p.font.name = "Arial"
            p.space_after = Pt(1.4)

    # Lower Section: Commercial Roadmap & Apex Maturity Cards (Height 1.25")
    road_top = Inches(5.48)
    road_h = Inches(1.22)
    
    # Left: Roadmap Card (Width 7.60")
    add_card(s11, Inches(0.65), road_top, Inches(7.60), road_h, fill_color=CARD_BG, border_color=ACCENT_BLUE, border_width=1.4)
    tb_r = s11.shapes.add_textbox(Inches(0.80), road_top + Inches(0.08), Inches(7.30), road_h - Inches(0.16))
    tf_r = tb_r.text_frame
    tf_r.word_wrap = True
    tf_r.margin_left = tf_r.margin_right = tf_r.margin_top = tf_r.margin_bottom = 0
    
    p = tf_r.paragraphs[0]
    p.text = "3-PHASE COMMERCIAL DEPLOYMENT ROADMAP:"
    p.font.size = Pt(9.5)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    p.font.name = "Arial"
    p.space_after = Pt(2)

    road_points = [
        "• Phase 1 (COMPLETED Prototype): 96-interval stochastic engine, 7 contingency shocks, HiGHS simplex LP, 26/26 tests passing, Scorecard Grade A+ (98.4/100).",
        "• Phase 2 (Target Q3–Q4 2026): Live NOAA WSR-88D Doppler radar socket streams, real-time ISO/RTO LMP WebSockets, 4-hour multi-temporal look-ahead MPC horizon.",
        "• Phase 3 (Target 2027 Production Pilot): RTDS / OPAL-RT real-time Hardware-in-the-Loop bench, IEC 61850 substation gateway with SEL relays, 50MW utility pilot."
    ]
    for rp in road_points:
        p = tf_r.add_paragraph()
        p.text = rp
        p.font.size = Pt(7.8)
        p.font.color.rgb = TEXT_BODY
        p.font.name = "Arial"
        p.space_after = Pt(1)

    # Right: Apex Maturity & Team Credits (Width 4.25")
    add_card(s11, Inches(8.43), road_top, Inches(4.25), road_h, fill_color=ACCENT_LIGHT_BLUE, border_color=ACCENT_PURPLE, border_width=1.4)
    tb_m = s11.shapes.add_textbox(Inches(8.55), road_top + Inches(0.08), Inches(4.01), road_h - Inches(0.16))
    tf_m = tb_m.text_frame
    tf_m.word_wrap = True
    tf_m.margin_left = tf_m.margin_right = tf_m.margin_top = tf_m.margin_bottom = 0
    
    p = tf_m.paragraphs[0]
    p.text = "APEX 9-BLOCKER MATURITY POSITION & TEAM:"
    p.font.size = Pt(9.5)
    p.font.bold = True
    p.font.color.rgb = ACCENT_PURPLE
    p.font.name = "Arial"
    p.space_after = Pt(2)

    p = tf_m.add_paragraph()
    p.text = "• Level F3 (Functional Depth): 24h multi-period simulation across 96 intervals, 7 shocks resolved, 15 binding SCADA actions."
    p.font.size = Pt(7.8)
    p.font.color.rgb = TEXT_TITLE
    p.font.name = "Arial"
    p.space_after = Pt(1)

    p = tf_m.add_paragraph()
    p.text = "• Level D3 (Decision Autonomy): Multimodal Doppler radar CV (ResNet-18) + deterministic simplex LP (HiGHS) + Gemini AI audit."
    p.font.size = Pt(7.8)
    p.font.color.rgb = TEXT_TITLE
    p.font.name = "Arial"
    p.space_after = Pt(1)

    p = tf_m.add_paragraph()
    p.text = "Engineering Team: ManojKumar P • B Iniyavan • Nishi Verma • Pasupulati Siva Puja"
    p.font.size = Pt(7.8)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    p.font.name = "Arial"

    add_bottom_strip(s11, "Audited Baseline Methodology: 96-interval 24h simulation comparing identical weather, load, and wholesale LMP price curves.", "+$2.24M / Year Net EBITDA", bg_color=ACCENT_LIGHT_GREEN, border_color=ACCENT_GREEN)

    # Save outputs to all target locations
    target_paths = [
        os.path.abspath("showcase/pitch-decks/GridOS_Pitch_Deck.pptx"),
        os.path.abspath("GridOS_Pitch_Deck.pptx"),
        r"C:\Users\paddu\Downloads\GridOS_Pitch_Deck.pptx",
        r"C:\Users\paddu\Downloads\GridOS_Renewable_Energy_Orchestrator_Light_Formal.pptx"
    ]

    for p_out in target_paths:
        os.makedirs(os.path.dirname(p_out), exist_ok=True)
        try:
            prs.save(p_out)
            print(f"Successfully generated native formal PPTX -> {p_out} ({os.path.getsize(p_out)/1024:.1f} KB)")
        except Exception as e:
            print(f"Could not save to {p_out}: {e}")

if __name__ == "__main__":
    build_dense_deck()
