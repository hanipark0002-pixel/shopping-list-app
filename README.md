# Shopping List App

로컬스토리지 기반 쇼핑 리스트 웹 앱입니다.

## 실행 방법

`shopping-list.html` 파일을 브라우저에서 직접 열면 됩니다.

## 기능

- 아이템 추가 (버튼 클릭 또는 Enter 키)
- 완료 체크 / 해제
- 아이템 삭제
- 필터 (전체 / 미완료 / 완료)
- 완료 항목 일괄 삭제
- 로컬스토리지 자동 저장 (새로고침 후에도 유지)

## 테스트

Playwright 기반 테스트 포함:

```bash
pip install playwright
playwright install chromium
python test_shopping.py
```
