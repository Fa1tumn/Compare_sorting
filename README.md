# Compare Sorting

GitHub repository: https://github.com/Fa1tumn/Compare_sorting

삽입 정렬·병합 정렬·힙 정렬을 직접 구현하고 같은 입력으로 성능을 비교하는 과제 프로젝트입니다. Python 3.10 이상을 사용합니다. 정렬과 벤치마크는 표준 라이브러리만 필요합니다.

## 실행

```powershell
python -m unittest -v
python benchmark.py
python -m pip install -r requirements.txt
python build_report.py
```

기본 실험: 입력 크기 100/500/1000/3000/6000, 5개 분포, 각 7회, 총 525회. 입력 생성 및 복사와 검증은 시간에서 제외하며, 정렬 중 보조 배열 할당은 포함합니다. 원시 데이터와 환경은 `results/`에 저장됩니다. 재실행하면 기존 측정값을 덮어씁니다.

```powershell
python benchmark.py --sizes 100 500 1000 --repeats 5 --seed 1234
```

`build_report.py`의 설명은 기본 실험 설정을 기준으로 작성되었습니다. 실험 개수나 반복 수를 바꾸면 보고서의 고정 설명도 검토해야 합니다.

## 파일

- `sorting.py`: 정렬 구현
- `test_sorting.py`: 경계값, 전수·난수 입력 및 안정성 검증
- `benchmark.py`: 재현 가능한 측정
- `results/raw.csv`: 개별 실행 시간(ns), 입력 시드
- `results/summary.csv`: 중앙값·사분위수·최솟값·최댓값(ms)
- `results/environment.json`: 측정 환경
- `build_report.py`: 한글 PDF 및 Markdown 생성
- `report/REPORT.md`: 보고서 원문
- `output/pdf/compare_sorting_report.pdf`: 보고서 PDF
- `submission.json`: 보고서에 넣을 이름·학번·저장소 URL

Windows 맑은 고딕을 사용합니다. 다른 환경에서는 `REPORT_FONT`, `REPORT_FONT_BOLD` 환경 변수에 한글 TTF 경로를 지정합니다.

## 제출 전 필수 작업

1. 코드를 읽고 실행 결과와 힙 정렬 설명을 검토합니다. 초안에는 AI 도움을 공개했습니다.
2. 본인의 GitHub 저장소를 만들고 URL을 확보합니다.
3. `submission.json`의 세 값을 입력하고 `python build_report.py`를 실행합니다.
4. 코드·결과·보고서를 저장소에 업로드합니다. `.deps`, `tmp`, `__pycache__`는 제외합니다.
5. GitHub 저장소의 **Code > Download ZIP**으로 ZIP을 받습니다. 로컬에서 만든 ZIP은 이 제출 조건을 대신하지 않습니다.
6. PDF와 GitHub에서 받은 ZIP을 제출하고, 보고서에 본인 저장소 URL이 있는지 확인합니다.

제출 기한: 2026-09-30 23:59. 이후 감점, 2026-10-02 23:59 이후 접수 불가. 제출 플랫폼의 시간 기준을 따릅니다.

## 참고

- 과제 샘플: https://github.com/lec-algorithm/hw1-sample-2026
- 과제 지정 분류표: https://en.wikipedia.org/wiki/Sorting_algorithm#Comparison_of_algorithms
- 힙 원리: https://algs4.cs.princeton.edu/24pq/
