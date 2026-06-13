"""Build all 12 FP&A handoff charts into one deck + export PNGs via PowerPoint COM.
Run from design-system/pptx/ :  python _build_fpna_charts.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from deck_system import PresentationBuilder, MODERN

b = PresentationBuilder(theme=MODERN)
b.add("bullet", title="FY26 핵심 KPI, 목표 대비 실적", source="FP&A 내부 결산 (예시)", items=[
    {"label": "매출", "measure": 1430, "target": 1200, "ranges": [800, 1100, 1500], "unit": "억"},
    {"label": "영업이익", "measure": 168, "target": 200, "ranges": [120, 180, 240], "unit": "억"},
    {"label": "FCF 전환율", "measure": 84, "target": 80, "ranges": [50, 70, 100], "unit": "%"},
    {"label": "상위3사 집중도", "measure": 58, "target": 45, "ranges": [40, 60, 80], "unit": "%"}])
b.add("tornado", title="민감도 분석 — 영업이익 변동폭", base=200, unit="억", items=[
    {"label": "물동량 ±10%", "low": 158, "high": 246}, {"label": "인건비 ±8%", "low": 176, "high": 224},
    {"label": "연료비 ±15%", "low": 184, "high": 216}, {"label": "환율 ±5%", "low": 190, "high": 210}])
b.add("pvm_bridge", title="FY26 매출 +180억, 가격·물량 견인 / 믹스 악화", unit="억", items=[
    {"label": "FY25 매출", "value": 1200, "type": "base"}, {"label": "가격 효과", "value": 145, "type": "price"},
    {"label": "물량 효과", "value": 90, "type": "volume"}, {"label": "믹스 효과", "value": -55, "type": "mix"},
    {"label": "FY26 매출", "value": 1380, "type": "end"}])
b.add("cohort_heatmap", title="코호트 잔존율 — 6개월차 평균 55%",
      periods=["M0", "M1", "M2", "M3", "M4", "M5", "M6"], cohorts=[
    {"label": "25-01", "values": [100, 82, 71, 65, 60, 57, 55]},
    {"label": "25-02", "values": [100, 79, 68, 61, 56, 53, None]},
    {"label": "25-03", "values": [100, 85, 74, 68, 63, None, None]},
    {"label": "25-04", "values": [100, 80, 70, 64, None, None, None]},
    {"label": "25-05", "values": [100, 83, 73, None, None, None, None]},
    {"label": "25-06", "values": [100, 78, None, None, None, None, None]}])
b.add("combo", title="매출 성장과 수익성 — Q4 동반 개선", categories=["Q1", "Q2", "Q3", "Q4"],
      bars={"label": "매출", "values": [1100, 1250, 1180, 1430], "unit": "억"},
      line={"label": "영업이익률", "values": [11.2, 13.4, 9.8, 14.3], "unit": "%"})
b.add("driver_tree", title="ROIC 14.0% 분해 — 수익성 × 자산회전",
      root={"label": "ROIC", "value": "14.0%"}, children=[
    {"label": "영업이익률", "value": "8.0%", "op": "×", "children": [
        {"label": "매출", "value": "1,430억"}, {"label": "영업이익", "value": "114억"}]},
    {"label": "자산회전율", "value": "1.75x", "op": "", "children": [
        {"label": "매출", "value": "1,430억"}, {"label": "투하자본", "value": "817억"}]}])
b.add("scatter", title="물량-원가 상관 — 규모의 경제 확인", x_label="처리물량(천건)", y_label="건당원가(원)", trend=True,
      points=[{"x": 120, "y": 840}, {"x": 185, "y": 720}, {"x": 240, "y": 660}, {"x": 310, "y": 590},
              {"x": 360, "y": 560}, {"x": 420, "y": 520}, {"x": 480, "y": 505}])
b.add("scenario_summary", title="시나리오 분석 — Upside 250억 vs Downside 120억",
      scenarios=["Downside", "Base", "Upside"], metrics=[
    {"label": "매출", "values": [1100, 1300, 1500], "unit": "억"},
    {"label": "영업이익", "values": [120, 180, 250], "unit": "억"},
    {"label": "영업이익률", "values": [10.9, 13.8, 16.7], "unit": "%"}])
b.add("overlapping_line", title="월별 계절성 — 11~12월 성수기 3년 연속",
      months=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"], unit="억", series=[
    {"year": "2023", "values": [80, 75, 90, 95, 88, 92, 98, 110, 105, 120, 140, 165]},
    {"year": "2024", "values": [88, 82, 98, 103, 96, 101, 108, 121, 116, 132, 154, 182]},
    {"year": "2025", "values": [95, 90, 107, 112, 105, 110, 118, 132, 127, 144, 168, 198]}])
b.add("heatmap", title="부서별 월간 비용 변동률 — 마케팅 변동성 최대",
      rows=["물류", "영업", "마케팅", "개발", "지원"], cols=["1월", "2월", "3월", "4월", "5월", "6월"],
      unit="%", diverging=True, center=0, values=[
    [2.1, -3.4, 5.2, -1.1, 4.8, -2.2], [-5.5, 3.1, -2.0, 6.3, -4.1, 2.7],
    [8.2, -6.1, 1.4, -3.8, 5.5, -7.0], [-1.2, 4.4, -5.6, 2.9, -3.3, 6.1],
    [3.0, -2.5, 4.1, -1.9, 2.2, -4.4]])
b.add("treemap", title="영업비용 구성 — 인건비·물류비가 2/3", unit="억", items=[
    {"label": "인건비", "value": 420}, {"label": "물류비", "value": 310}, {"label": "마케팅비", "value": 180},
    {"label": "임차료", "value": 130}, {"label": "R&D", "value": 110}, {"label": "감가상각", "value": 95},
    {"label": "기타", "value": 75}])
b.add("breakeven", title="손익분기 분석 — BEP 200개, 이상부터 흑자",
      fixed_cost=4000, unit_price=50, unit_var_cost=30, max_volume=400, unit="만원", vol_unit="개")

out_pptx = os.path.abspath("out/fpna-charts-all.pptx")
b.save(out_pptx)
print("BUILD OK:", out_pptx)

# Export each slide to PNG via PowerPoint COM (LibreOffice not used)
try:
    import win32com.client
    review = os.path.abspath(os.path.join("..", "..", "_review"))
    names = ["pptx-1-bullet", "pptx-2-tornado", "pptx-3-pvm", "pptx-4-cohort", "pptx-5-combo",
             "pptx-6-driver-tree", "pptx-7-scatter", "pptx-8-scenario", "pptx-9-overlapping",
             "pptx-10-heatmap", "pptx-11-treemap", "pptx-12-breakeven"]
    ppt = win32com.client.Dispatch("PowerPoint.Application")
    deck = ppt.Presentations.Open(out_pptx, WithWindow=False)
    n = deck.Slides.Count
    for i in range(1, n + 1):
        png = os.path.join(review, names[i - 1] + ".png")
        deck.Slides(i).Export(png, "PNG", 1280, 720)
    deck.Close()
    ppt.Quit()
    print(f"PNG OK: {n} slides exported to _review/")
except Exception as e:
    print("PNG export skipped:", e)
