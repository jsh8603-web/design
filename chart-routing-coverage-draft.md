# 차트/양식 라우팅 — 상황별 커버리지 초안 (자문 R3 점검용)

> 목적: FP&A 에이전트가 "이 상황 → 이 양식" 헷갈리지 않게. 자문 점검 = (1) 오매핑 (2) 빠진 가지(커버 안 되는 상황) (3) 한 상황에 여러 양식 겹쳐 혼동.
> 도구: Excel(계산 28템플릿) / Slide(시각 64+4레이아웃). 신규 4종 = bullet·tornado·pvm_bridge·cohort_heatmap.

## Gate 0 — 진입 게이트 (양식 문제 아님, Excel 운영경로)
- 더러운 엑셀 정리 요청 → `ingest`
- 스키마만 반출 → `profile`
- 암호화 운반 → `transport`
- 그 외 → analysis (↓ 의도 트리 진입)

## 의도 패밀리 A — 정량 메시지 (공통 trunk: Excel 계산 ↔ Slide 시각 페어)
> 분기질문: "결과 숫자를 다시 만지나? Yes→Excel단말 / No(확정결론 보여주기)→Slide단말". Slide경로에 분해값 없으면 Excel 선행.

| 상황 (이럴 때) | Excel 단말 | Slide 단말 |
|---|---|---|
| 예산 대비 실적 차이를 항목별로 | variance | variance_table |
| 시작→끝 누적 증감 다리 | variance/fc_variance_bridge | waterfall |
| 가격·물량·믹스 3요인 분해 | pvm_bridge | pvm_bridge(slide 신규) |
| 가정 변수 민감도 양방향 | scenario_sensitivity | tornado(신규) |
| 단일 핵심 숫자 강조 | — | big_number |
| 단일 지표 목표/구간 위치 | — | gauge |
| 다수 KPI 목표대비 정밀(실적/목표/밴드) | board_kpi_pack | bullet(신규) |
| 다수 KPI 판정만(R/A/G) | board_kpi_pack | scorecard |
| 다수 KPI 단위 제각각 타일 개요 | board_kpi_pack | kpi_dashboard / dashboard_kpi |
| 시간 흐름 추세 | period_trend | line_chart |
| 시점별 크기 비교(과거+예측) | period_trend | column_historic_forecast / column_simple_growth |
| 구성비 추이(부분합) | period_trend | stacked_area(연속) / stacked_column(이산) |
| 전망 갱신 롤링 | rolling_forecast | line_chart + forecast 구간 |
| 코호트 잔존율 그리드 | cohort_retention | cohort_heatmap(신규) |
| 항목 순위/파레토 80:20 | — | pareto / horizontal_bar |
| 단일 전체 구성비(파이) | — | donut(중앙총계) / pie |
| 2~3변수 분포 버블 | — | bubble |

## 의도 패밀리 B — 모델/스케줄 구축 (Excel 곁가지, Slide는 요약결과만)
| 상황 | Excel 단말 |
|---|---|
| 투자 타당성 NPV/IRR/회수 | investment_appraisal |
| 13주 단기 현금/유동성 | cashflow_13w |
| 운전자본 DSO/DPO/CCC | working_capital |
| 듀폰 ROE/ROIC 분해 | dupont_roic |
| 부채 스케줄/리볼버/캐시스윕 | debt_schedule |
| 리스 자본화 IFRS16 | fc_lease_ifrs16 |
| 감가상각 스케줄 | fc_depreciation_schedule |
| 미래 감가 투영(CAPEX연계) | fc_forward_da |
| 단계식 배부(step-down) | fc_allocation / cost_allocation |
| 만기 도래 벽 | fc_maturity_wall |
| 런레이트 정규화 | fc_runrate_normalized |
| 선급비용 롤포워드 | fc_prepaid_rollforward |
| 비용 절감 가능성 계층 | fc_cuttability_ladder |
| 동인별 단위원가 | fc_driver_unitcost |
| 인원/인건비 계획 | headcount_plan |
| 단위경제 CAC/LTV | unit_economics |
| 연결/환산 FX | consolidation_fx |
| 예산 편성 | budget_build |
| 손익 3-statement | pnl_3statement |

## 의도 패밀리 C — 개념 프레임 / 내러티브 (Slide 곁가지, Excel 불필요)
| 상황 | Slide 단말 |
|---|---|
| 같은 대상 개입 전/후 | before_after |
| 단일 결정 장단 저울질 | pros_cons |
| 복수 대안 속성 격자 비교 | comparison_table |
| 2~3 옵션 패널/카드(이질) | side_by_side |
| 내부/외부×긍정/부정 4버킷 | swot |
| 발생가능성×영향 리스크 | risk_matrix |
| 시장성장×점유율 포트폴리오 | bcg_matrix |
| 임팩트×노력 우선순위 | prioritization_matrix |
| 순차 단계(수평/수직) | phases_chevron / vertical_steps |
| 깔때기 전환 | funnel |
| 순환 PDCA | cycle |
| 가치사슬 | value_chain |
| 계층 피라미드 | pyramid |
| 일정 간트 | gantt_timeline / waves_timeline / timeline |
| 조직도 | org_chart |
| 표+인사이트 캡슐 | table_insight |
| 인용/선언 | quote |
| 2~5개 통계/트렌드/영역 요약 | two_stat/three_stat/three_trends/five_key_areas |
| 개념 교집합 | venn |
| 프레임워크 기둥(비전) | temple |

## 구조 슬라이드 (덱 골격, 의도 무관)
cover · section_divider · toc/agenda · executive_summary · key_takeaway · closing · appendix_title · dark_navy_summary

## ★ 자문 점검 요청 (R3 핵심)
1. **오매핑**: 위 표에서 "이 상황엔 이 양식이 아니라 저 양식"인 곳?
2. **빠진 가지**: FP&A 실무에서 자주 있는데 위 어느 행에도 안 들어가는 상황? (커버리지 구멍)
3. **혼동 겹침**: 한 상황에 후보가 2개+라 에이전트가 헷갈릴 곳 + 변별 단일질문.
4. **공통가지 페어 정합**: Excel단말↔Slide단말 페어가 데이터 핸드오프로 실제 이어지나(Excel 출력 spec → Slide 입력 spec).
