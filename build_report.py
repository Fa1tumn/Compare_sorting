"""Build a five-page Korean PDF and Markdown report from measured CSV data."""
import csv
import json
import os
import sys
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent
sys.path.append(str(ROOT / ".deps"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image


def main():
    os.chdir(ROOT)
    rows = list(csv.DictReader(open("results/summary.csv", encoding="utf-8")))
    env = json.loads(Path("results/environment.json").read_text(encoding="utf-8"))
    identity = json.loads(Path("submission.json").read_text(encoding="utf-8"))
    sizes = sorted({int(r["n"]) for r in rows})
    largest = max(sizes)
    run_count = env['validated_runs']
    repeat_count = env['parameters']['repeats']
    index = {(r["pattern"], int(r["n"]), r["algorithm"]): r for r in rows}
    def ms(pattern, n, algorithm):
        return float(index[pattern, n, algorithm]["median_ms"])
    names = {"insertion": "삽입", "merge": "병합", "heap": "힙"}
    patterns = {"random": "무작위", "sorted": "정렬됨", "reversed": "역순",
                "nearly_sorted": "거의 정렬됨", "duplicates": "중복 많음"}
    Path("report").mkdir(exist_ok=True)
    Path("output/pdf").mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.3))
    for ax, pattern in zip(axes, ("random", "sorted")):
        for algo in names:
            ax.plot(sizes, [ms(pattern, n, algo) for n in sizes], marker="o", label=algo)
        ax.set(xscale="log", yscale="log", xlabel="Input size (n)", ylabel="Median time (ms)", title=pattern)
        ax.grid(alpha=.25)
        ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig("report/timing.png", dpi=180)
    plt.close(fig)
    font = os.environ.get("REPORT_FONT", "C:/Windows/Fonts/malgun.ttf")
    bold = os.environ.get("REPORT_FONT_BOLD", "C:/Windows/Fonts/malgunbd.ttf")
    pdfmetrics.registerFont(TTFont("KR", font))
    pdfmetrics.registerFont(TTFont("KR-Bold", bold))
    style = ParagraphStyle("body", fontName="KR", fontSize=9.6, leading=16, wordWrap="CJK", spaceAfter=9)
    heading = ParagraphStyle("heading", parent=style, fontName="KR-Bold", fontSize=16, leading=23, textColor=colors.HexColor("#173B60"), spaceAfter=16)
    subheading = ParagraphStyle("subheading", parent=style, fontName="KR-Bold", fontSize=11, leading=17, spaceBefore=8)
    tiny = ParagraphStyle("tiny", parent=style, fontSize=8, leading=12)
    cell = ParagraphStyle("cell", parent=style, fontSize=8.4, leading=12, spaceAfter=0)
    story, md = [], []
    def h(text):
        story.append(Paragraph(escape(text), heading)); md.append("# " + text + "\n")
    def s(text):
        story.append(Paragraph(escape(text), subheading)); md.append("## " + text + "\n")
    def p(text, small=False):
        story.append(Paragraph(escape(text).replace('\n', '<br/>'), tiny if small else style)); md.append(text + "\n")
    def table(data, widths):
        rendered = [[Paragraph(escape(str(v)).replace('\n', '<br/>'), cell) for v in row] for row in data]
        t = Table(rendered, colWidths=[w * mm for w in widths], repeatRows=1)
        t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E5EEF6")),
                               ("VALIGN", (0, 0), (-1, -1), "TOP"),
                               ("GRID", (0, 0), (-1, -1), .4, colors.HexColor("#CCD5DF")),
                               ("TOPPADDING", (0, 0), (-1, -1), 7),
                               ("BOTTOMPADDING", (0, 0), (-1, -1), 7)]))
        story.extend([t, Spacer(1, 10)])
        def md_cell(value):
            return str(value).replace('|', '\\|').replace('\n', '<br>')
        md.append("\n".join(["| " + " | ".join(map(md_cell, data[0])) + " |",
                             "| " + " | ".join(["---"] * len(data[0])) + " |"] +
                            ["| " + " | ".join(map(md_cell, r)) + " |" for r in data[1:]]) + "\n")
    def page():
        story.append(PageBreak()); md.append("\n---\n")

    h("정렬 비교 보고서")
    p("삽입 정렬 · 병합 정렬 · 힙 정렬 | 과제 1 | 2026년 9월 29일")
    p(f"이름: {identity['name'] or '미제공'}    학번: {identity['student_id'] or '미제공'}")
    p("GitHub 저장소: " + (identity["repository_url"] or "미제공 - 제출 전 본인 저장소 URL을 입력해야 함"))
    if not all(identity.values()):
        p("상태: 제출 정보 미입력 초안. 실험 결과는 실제 실행 결과이며, 제출자 정보와 저장소 URL을 반영한 뒤 PDF를 다시 생성해야 한다.")
    s("1. 비교 목적과 선정 이유")
    p("수업에서 배운 삽입 정렬과 병합 정렬, 제시된 수업 목록에 없는 힙 정렬을 비교한다. 삽입 정렬은 입력이 이미 정렬되어 있을 때 빠르지만 이동량이 많으면 느려진다. 병합 정렬은 추가 배열을 사용하여 입력 순서의 영향을 줄인다. 힙 정렬은 배열 안에서 최대 원소를 반복해서 꺼내므로 최악 시간과 추가 공간을 함께 살펴보기 좋다.")
    p("핵심 질문은 ‘항상 가장 빠른 정렬이 있는가?’이다. 입력 크기와 정렬 상태를 바꾸면서 실행 시간을 측정하고, 안정성과 추가 공간은 코드 구조 및 별도 정확성 검사로 비교한다. 내장 sorted()는 정답 검증에만 사용하며 비교 대상 알고리즘 구현에는 사용하지 않았다.")
    s("2. 구현 기준 이론 비교")
    table([["알고리즘", "최선 / 평균 / 최악 시간", "추가 공간", "안정성"],
           ["삽입", "O(n) / O(n²) / O(n²)", "O(1)", "안정"],
           ["병합", "O(n log n) / O(n log n) / O(n log n)", "O(n)", "안정"],
           ["힙", "O(n)* / O(n log n) / O(n log n)", "O(1)", "불안정"]], [24, 83, 27, 28])
    p("* 힙 정렬의 최선 O(n)은 모든 키가 같은 입력에서 본 구현의 sift_down이 즉시 종료하는 경우이다. 서로 다른 키에 대한 일반적인 힙 정렬 설명과 구별한다. 평균 시간은 무작위 입력에 대한 통상적 분석이며, O 표기는 점근적 상한이다. 병합 정렬에는 이미 정렬된 구간을 건너뛰는 최적화를 넣지 않았다.", small=True)
    p("안정 정렬은 같은 키를 가진 원소의 원래 순서를 유지한다. 추가 공간에는 입력 배열을 포함하지 않는다. 병합 정렬은 길이 n의 보조 배열과 O(log n) 재귀 스택을 사용하므로 전체 추가 공간은 O(n)이다.")

    page(); h("3. AI 학습 첨부: 힙 정렬")
    p("아래는 이 과제를 준비하면서 AI가 작성한 학습 설명이다. 학생이 별도로 이해도를 확인했다는 진술이나 실제 사용자 질문 기록은 아니다. 코드·실험·초안 작성에도 AI 도움을 사용했으며, 제출자는 구현과 결과를 직접 검토해야 한다.")
    s("학습 주제 1 | 힙은 정렬된 배열인가?")
    p("최대 힙은 모든 부모의 값이 자식 값 이상인 완전 이진 트리이다. 루트가 가장 크다는 사실은 보장되지만, 형제끼리나 배열 전체가 정렬되어 있지는 않다. 0부터 시작하는 배열에서 인덱스 i의 왼쪽 자식은 2i+1, 오른쪽 자식은 2i+2이므로 별도 트리 노드가 없어도 구현할 수 있다.")
    s("학습 주제 2 | 어떻게 오름차순으로 정렬하는가?")
    p("① 마지막 부모 n//2-1부터 루트까지 sift_down을 수행하여 최대 힙을 만든다. ② 루트와 현재 힙의 마지막 원소를 교환한다. ③ 방금 놓은 최댓값을 힙에서 제외한다. ④ 루트에서 더 큰 자식 방향으로 내려가며 힙 조건을 회복한다. 남은 힙의 크기가 1이 될 때까지 반복한다.")
    table([["단계", "배열 상태 (| 오른쪽은 확정된 영역)"],
           ["입력", "[4, 1, 3, 2]"],
           ["최대 힙 구성", "[4, 2, 3, 1]"],
           ["4를 뒤로 이동 후 복구", "[3, 2, 1 | 4]"],
           ["3을 뒤로 이동 후 복구", "[2, 1 | 3, 4]"],
           ["마지막 교환", "[1 | 2, 3, 4]"]], [53, 109])
    s("학습 주제 3 | 힙 구성은 왜 O(n)인가?")
    p("모든 노드가 트리 높이만큼 내려가지는 않는다. 절반 정도는 리프이고, 아래쪽 노드일수록 내려갈 거리가 짧다. 높이 h인 노드가 대략 n/2^(h+1)개이므로 전체 작업량은 n × Σ(h/2^(h+1))에 비례하고 O(n)이다. 이후 최대 n-1번의 추출은 각각 O(log n)이라 전체 최악 시간은 O(n log n)이 된다. 이 설명은 Princeton의 힙 구성·정렬 설명 [2]로 확인했다.")
    s("학습 주제 4 | 공간과 안정성의 대가는?")
    p("본 구현은 sift_down을 반복문으로 작성하여 추가 공간이 O(1)이다. 다만 떨어진 두 원소를 교환하므로 안정적이지 않다. 키만 비교할 때 [2A, 2B, 1C]는 [1C, 2B, 2A]가 되어 같은 키 2의 순서가 바뀐다. 이 반례는 테스트로도 확인했다. 동일 키의 입력 순서를 유지해야 하는 문제라면 이 구현의 힙 정렬은 적합하지 않다.")

    page(); h("4. 실험 설계와 검증")
    s("동일 조건으로 측정하기")
    p(f"입력 크기는 {', '.join(map(str, sizes))}이고, 각 크기·분포마다 {env['parameters']['repeats']}회 측정했다. 기본 난수 시드는 {env['parameters']['seed']}이다. 반복마다 재현 가능한 다른 시드를 사용하되, 세 정렬에는 같은 원본의 복사본을 주었다. 정렬됨·역순은 반복 간 내용이 같고 나머지 분포는 난수가 달라진다.")
    table([["입력 분포", "생성 방법"], ["무작위", "0부터 n-1까지의 서로 다른 정수를 섞음"],
           ["정렬됨 / 역순", "0..n-1 오름차순 / n-1..0 내림차순"],
           ["거의 정렬됨", "오름차순 배열에서 max(1, n//100)번 임의 두 위치 교환"],
           ["중복 많음", "각 위치에 0..9 중 하나를 균등하게 생성"]], [38, 124])
    p("각 알고리즘을 n=100 무작위 입력으로 3회 예열한 뒤, 매 반복의 실행 순서를 섞었다. perf_counter_ns()로 정렬 함수 호출만 측정했다. 입력 생성·복사·정답 생성·검증·파일 쓰기는 측정에서 제외했고, 정렬 내부 보조 배열 할당은 포함했다. 측정 중 순환 가비지 수집은 중지한 뒤 원래 상태로 복원했다.")
    p(f"대표값은 중앙값이며, 표의 Q1-Q3는 {repeat_count}개 측정값의 inclusive 방식 사분위수이다. 이는 신뢰구간이 아니다. 난수 입력의 차이와 운영체제 실행 편차가 함께 포함된다. 입력 크기별 동일 조건의 총 {run_count}개 정렬 결과를 sorted()의 결과와 비교해 값과 중복 개수까지 검증했다.")
    s("실행 환경")
    p(f"Python: {env['python'].splitlines()[0]}\n운영체제: {env['platform']}\n프로세서 식별: {env['processor']} / 논리 프로세서 {env['logical_cpus']}개", small=True)
    p(f"측정 시각(UTC): {env['timestamp']}. CPU 고정·부하 격리·주파수 고정은 수행하지 않았다. 따라서 수치는 이 환경에서 얻은 관측값이며 다른 컴퓨터에서 동일한 절대 시간이 재현된다고 보장하지 않는다.", small=True)
    s("정확성 및 안정성 테스트")
    p("unittest의 5개 테스트 메서드가 통과했다. 빈 배열·단일 값·음수·중복·정렬·역순을 확인했고, {-1, 0, 1}로 만들 수 있는 길이 0..6의 모든 1,093개 배열과 난수 배열 100개를 각 정렬로 검사했다. (키, 원래 위치) 객체로 삽입·병합의 안정성을 확인했으며, 힙의 불안정성은 앞쪽 반례로 재현했다. 유한한 테스트는 모든 입력에 대한 수학적 증명을 대신하지 않는다.")

    page(); h("5. 실제 측정 결과")
    p(f"아래 값은 n={largest:,}에서의 실행 시간이다. 단위는 ms이며 각 칸은 중앙값 [Q1-Q3]이다. 전체 {len(rows)}개 조합의 요약은 results/summary.csv, 원시 {run_count}개 관측값은 results/raw.csv에 저장했다.")
    data = [["입력", "삽입", "병합", "힙"]]
    for pattern, label in patterns.items():
        values = [label]
        for algo in names:
            r = index[pattern, largest, algo]
            values.append(f"{float(r['median_ms']):.3f}\n[{float(r['q1_ms']):.3f}-{float(r['q3_ms']):.3f}]")
        data.append(values)
    table(data, [33, 43, 43, 43])
    s("입력 크기에 따른 변화")
    story.append(Image("report/timing.png", width=164 * mm, height=54.12 * mm))
    md.append("![입력 크기별 중앙 실행 시간](timing.png)\n")
    p("그림 1. 무작위 입력(왼쪽)과 정렬된 입력(오른쪽)의 중앙 실행 시간. 두 축은 모두 로그 척도다. 작은 입력에서는 타이머·함수 호출 비용과 시스템 잡음의 비중이 커지므로 작은 차이를 일반화하지 않는다.", small=True)
    s("관측값 읽기")
    ratio = ms("random", largest, "insertion") / ms("random", largest, "merge")
    sorted_ratio = ms("sorted", largest, "merge") / ms("sorted", largest, "insertion")
    p(f"무작위 n={largest:,}에서 삽입 정렬은 병합 정렬보다 약 {ratio:.1f}배의 시간이 걸렸다. 반면 정렬된 입력에서 병합 정렬의 시간은 삽입 정렬의 약 {sorted_ratio:.1f}배였다. 삽입 정렬은 이미 제자리에 있는 원소를 거의 이동하지 않으므로 입력 순서에 따라 결과가 크게 달라졌다.")
    prior = sizes[-2] if len(sizes) > 1 else sizes[-1]
    p(f"무작위 입력 크기를 {prior:,}에서 {largest:,}로 늘렸을 때 관측된 시간 배율은 삽입 {ms('random', largest, 'insertion')/ms('random', prior, 'insertion'):.2f}배, 병합 {ms('random', largest, 'merge')/ms('random', prior, 'merge'):.2f}배, 힙 {ms('random', largest, 'heap')/ms('random', prior, 'heap'):.2f}배였다. 유한한 크기의 관측값은 복잡도와 일치하는 경향을 살펴보는 근거이며 복잡도 자체의 증명은 아니다.")

    page(); h("6. 해석, 한계와 재현 방법")
    s("어떤 상황에 무엇을 선택할까?")
    p("삽입 정렬은 작은 입력이나 이미 정렬된 입력에서 유리하다. 거의 정렬된 경우에도 임의의 먼 두 위치를 교환하면 많은 역전 쌍이 생길 수 있으므로, ‘교환 횟수 1%’를 ‘전체 원소 중 정확히 1%만 잘못됨’으로 해석하면 안 된다. 역순에서는 각 원소가 앞부분을 통과해야 하므로 제곱 시간의 부담이 나타난다.")
    p("병합 정렬은 입력 분포가 달라져도 O(n log n) 수행을 유지하며 안정성이 필요할 때 적합하다. 그 대가로 길이 n의 보조 배열이 필요하다. 힙 정렬은 최악 O(n log n)과 O(1) 추가 공간이 장점이다. 같은 점근적 시간이라도 비교·교환 횟수, 인덱스 계산, Python 인터프리터 비용이 달라 실제 속도는 같지 않다. 본 실험만으로 특정 내부 비용이 속도 차이의 원인이라고 단정하지 않는다.")
    p("결론적으로 입력 특성·안정성 요구·메모리 제약을 함께 고려해야 한다. 이번 실험은 시간만 직접 측정했다. 공간 복잡도는 구현에서 분석한 결과이며 실제 최대 메모리를 측정한 값이 아니다. 비교 대상은 직접 작성한 세 Python 구현으로 한정되며, 다른 언어나 내장 정렬의 성능까지 설명하지 않는다.")
    s("재현 및 파일 구성")
    p("1. python -m unittest -v : 정답 및 안정성 검사\n2. python benchmark.py : 원시 시간·요약·환경 기록 생성\n3. python -m pip install -r requirements.txt : 보고서 의존성 설치\n4. submission.json에 이름·학번·GitHub URL 입력\n5. python build_report.py : Markdown과 PDF 재생성")
    p("sorting.py는 세 알고리즘, benchmark.py는 입력 생성과 측정, test_sorting.py는 검증을 담당한다. 보고서는 results 파일을 읽어 표·그래프·비율을 생성하므로 다시 측정하면 관측값이 함께 갱신된다. 기본 글꼴은 Windows 맑은 고딕이며, 다른 환경에서는 REPORT_FONT와 REPORT_FONT_BOLD로 한글 TTF 경로를 지정한다.")
    s("참고 자료와 AI 사용 공개")
    p("[1] Wikipedia, Sorting algorithm - Comparison of algorithms. 과제에서 지정한 분류와 추가 정렬 선택을 확인. https://en.wikipedia.org/wiki/Sorting_algorithm#Comparison_of_algorithms", small=True)
    p("[2] Robert Sedgewick · Kevin Wayne, Algorithms 4th Edition, §2.4 Priority Queues. 최대 힙, 선형 시간 힙 구성, 정렬 단계를 확인. https://algs4.cs.princeton.edu/24pq/", small=True)
    p("[3] 과제 샘플 저장소 및 보고서. 제출물 구성 참고. https://github.com/lec-algorithm/hw1-sample-2026 및 report/REPORT.md. 위 웹 자료 확인일: 2026-09-29.", small=True)
    p("AI 사용: 이 대화의 AI가 힙 정렬 학습 설명, 코드, 테스트 및 보고서 초안 작성을 지원했다. 실험 수치는 실제 프로그램 실행에서 얻었다. 제출 전 학생 본인의 설명·이해 확인과 저장소 정보 반영이 필요하다.", small=True)

    def footer(canvas, doc):
        canvas.setStrokeColor(colors.HexColor("#CCD5DF"))
        canvas.line(23 * mm, 18 * mm, 187 * mm, 18 * mm)
        canvas.setFont("KR", 8)
        canvas.drawString(23 * mm, 13 * mm, "Compare Sorting | 삽입 · 병합 · 힙")
        canvas.drawRightString(187 * mm, 13 * mm, str(doc.page))
    doc = SimpleDocTemplate("output/pdf/compare_sorting_report.pdf", pagesize=(210*mm, 297*mm),
                            rightMargin=23*mm, leftMargin=23*mm, topMargin=21*mm, bottomMargin=24*mm,
                            title="정렬 비교 보고서 - 삽입 · 병합 · 힙", author=identity["name"] or "")
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    Path("report/REPORT.md").write_text("\n".join(md), encoding="utf-8")
    print("Generated output/pdf/compare_sorting_report.pdf and report/REPORT.md")


if __name__ == "__main__":
    main()
