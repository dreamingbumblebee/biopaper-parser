# PDF 파서 with ChatGPT API 📄

이 프로그램은 ChatGPT API를 사용하여 PDF 파일에서 구조화된 데이터를 추출합니다. 여러 모델 선택과 비용 모니터링을 지원합니다.

## 설치 방법 🛠️

1. pyenv 설치 (이미 설치되어 있지 않은 경우):
```bash
# macOS
brew install pyenv pyenv-virtualenv

# Linux
curl https://pyenv.run | bash
```

2. pyenv로 Python 설치 및 가상환경(oai_extract) 생성:
```bash
# Python 3.11.8 설치
pyenv install 3.11.8

# 가상환경 생성 및 활성화
pyenv virtualenv 3.11.8 oai_extract
pyenv activate oai_extract

# pip 최신화 및 패키지 설치
pip install --upgrade pip
pip install -r requirements.txt
```

3. 프로젝트 루트에 `.env` 파일을 생성하고 OpenAI API 키를 추가합니다:
```
OPENAI_API_KEY=your_api_key_here
```

## 사용 방법 📝

### 사용 가능한 모델 확인

사용 가능한 모든 모델과 설명을 보려면:
```bash
python pdf_parser.py --list-models
```

### PDF 파일 처리

프로그램을 실행하는 두 가지 방법이 있습니다:

1. 현재 디렉토리의 모든 PDF 파일 처리:
```bash
python pdf_parser.py --model gpt-4.1-nano
```

2. 특정 PDF 파일 처리:
```bash
python pdf_parser.py --model gpt-4.1-nano pdf_sample.pdf
```

참고: 기본적으로 프로그램은 가장 비용 효율적인 모델(gpt-4.1-nano)을 사용합니다. 다른 모델을 사용하려면 --model 옵션을 변경하세요:
```bash
python pdf_parser.py --model gpt-4.1 file1.pdf
```

### 모델 선택

사용 가능한 모델:
- `gpt-4.1`: 복잡한 작업을 위한 가장 강력한 모델
- `gpt-4.1-mini`: 속도와 지능의 균형을 맞춘 합리적인 모델
- `gpt-4.1-nano`: 저지연 작업을 위한 가장 빠르고 비용 효율적인 모델
- `o3`: 코딩, 수학, 과학, 비전 분야에서 최고의 성능을 보이는 가장 강력한 추론 모델
- `o4-mini`: 수학, 코딩, 비전 분야에서 강력한 성능을 제공하는 빠르고 비용 효율적인 추론 모델

## 출력 결과 📊

프로그램은 두 가지 유형의 출력 파일을 생성합니다:

1. `results.jsonl`: PDF에서 추출한 데이터를 포함하며, 각 줄은 다음을 포함하는 JSON 객체입니다:
   - PDF에서 추출한 데이터
   - 파일 경로
   - 처리 비용
   - 처리 중 발생한 오류(있는 경우)

2. `cost_summary.json`: 모든 처리 비용의 요약을 포함합니다:
   - 총 비용
   - 모델별 비용
   - 파일별 비용
   - 타임스탬프

## 비용 모니터링 💰

프로그램은 자동으로 모든 API 비용을 추적하고 기록합니다:
- 상세 로그는 `logs` 디렉토리에 저장됩니다
- 비용 요약은 `cost_summary.json`에 저장됩니다
- 각 처리된 파일의 비용이 결과에 포함됩니다

## 오류 처리 ⚠️

처리 중 오류가 발생하면 출력 JSON에 오류 메시지가 포함된 "error" 필드가 포함됩니다.