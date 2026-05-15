import sys, pathlib
from playwright.sync_api import sync_playwright, expect

HTML_PATH = pathlib.Path(__file__).parent / "shopping-list.html"
URL = HTML_PATH.as_uri()

PASS = "[PASS]"
FAIL = "[FAIL]"

results = []

def log(status, name, detail=""):
    icon = PASS if status else FAIL
    msg = f"{icon} {name}"
    if detail:
        msg += f" -- {detail}"
    print(msg)
    results.append((status, name))


def run_tests():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=400)
        ctx = browser.new_context()
        ctx.clear_cookies()
        page = ctx.new_page()
        page.goto(URL)
        page.wait_for_load_state("domcontentloaded")

        # --- 1. 페이지 로드 ---
        try:
            title = page.locator("h1").inner_text()
            log(title == "Shopping List", "1. 페이지 로드", f"title='{title}'")
        except Exception as e:
            log(False, "1. 페이지 로드", str(e))

        # --- 2. 아이템 추가 (버튼 클릭) ---
        try:
            page.fill("#input", "사과")
            page.click("#btnAdd")
            item = page.locator(".item-text", has_text="사과")
            log(item.count() == 1, "2. 아이템 추가 (버튼)", "사과 추가됨")
        except Exception as e:
            log(False, "2. 아이템 추가 (버튼)", str(e))

        # --- 3. 아이템 추가 (Enter 키) ---
        try:
            page.fill("#input", "바나나")
            page.press("#input", "Enter")
            item = page.locator(".item-text", has_text="바나나")
            log(item.count() == 1, "3. 아이템 추가 (Enter)", "바나나 추가됨")
        except Exception as e:
            log(False, "3. 아이템 추가 (Enter)", str(e))

        # --- 4. 빈 입력 추가 시 무시 ---
        try:
            page.fill("#input", "   ")
            page.click("#btnAdd")
            count_before = page.locator(".item").count()
            page.fill("#input", "")
            page.click("#btnAdd")
            count_after = page.locator(".item").count()
            log(count_before == count_after, "4. 빈 입력 무시", f"아이템 수 유지={count_after}")
        except Exception as e:
            log(False, "4. 빈 입력 무시", str(e))

        # --- 5. 아이템 체크 (완료 표시) ---
        try:
            apple = page.locator(".item", has=page.locator(".item-text", has_text="사과"))
            checkbox = apple.locator(".checkbox")
            checkbox.click()
            page.wait_for_timeout(300)
            has_done = apple.get_attribute("class")
            log("done" in has_done, "5. 아이템 체크 (완료)", f"class='{has_done}'")
        except Exception as e:
            log(False, "5. 아이템 체크 (완료)", str(e))

        # --- 6. 아이템 체크 해제 ---
        try:
            apple = page.locator(".item", has=page.locator(".item-text", has_text="사과"))
            apple.locator(".checkbox").click()
            page.wait_for_timeout(300)
            has_done = apple.get_attribute("class")
            log("done" not in has_done, "6. 아이템 체크 해제", f"class='{has_done}'")
        except Exception as e:
            log(False, "6. 아이템 체크 해제", str(e))

        # --- 7. 아이템 삭제 ---
        try:
            banana = page.locator(".item", has=page.locator(".item-text", has_text="바나나"))
            banana.locator(".btn-delete").click()
            page.wait_for_timeout(300)
            remaining = page.locator(".item-text", has_text="바나나").count()
            log(remaining == 0, "7. 아이템 삭제", f"바나나 남은 수={remaining}")
        except Exception as e:
            log(False, "7. 아이템 삭제", str(e))

        # --- 8. 필터: 완료 탭 ---
        try:
            apple = page.locator(".item", has=page.locator(".item-text", has_text="사과"))
            apple.locator(".checkbox").click()
            page.wait_for_timeout(300)
            page.locator(".filter-btn[data-filter='done']").click()
            page.wait_for_timeout(300)
            visible = page.locator(".item-text", has_text="사과").count()
            log(visible == 1, "8. 필터 - 완료 탭", f"완료 아이템 보임={visible}")
        except Exception as e:
            log(False, "8. 필터 - 완료 탭", str(e))

        # --- 9. 필터: 미완료 탭 ---
        try:
            page.locator(".filter-btn[data-filter='active']").click()
            page.wait_for_timeout(300)
            visible = page.locator(".item-text", has_text="사과").count()
            log(visible == 0, "9. 필터 - 미완료 탭", f"완료 아이템 숨김={visible == 0}")
        except Exception as e:
            log(False, "9. 필터 - 미완료 탭", str(e))

        # --- 10. 필터: 전체 탭 복귀 ---
        try:
            page.locator(".filter-btn[data-filter='all']").click()
            page.wait_for_timeout(300)
            visible = page.locator(".item-text", has_text="사과").count()
            log(visible == 1, "10. 필터 - 전체 탭", f"전체 아이템 보임={visible}")
        except Exception as e:
            log(False, "10. 필터 - 전체 탭", str(e))

        # --- 11. 완료 일괄 삭제 ---
        try:
            page.locator("#btnClear").click()
            page.wait_for_timeout(300)
            remaining = page.locator(".item-text", has_text="사과").count()
            log(remaining == 0, "11. 완료 일괄 삭제", f"사과(완료) 삭제됨={remaining == 0}")
        except Exception as e:
            log(False, "11. 완료 일괄 삭제", str(e))

        # --- 12. 카운터 표시 ---
        try:
            page.fill("#input", "딸기")
            page.press("#input", "Enter")
            page.wait_for_timeout(200)
            count_text = page.locator("#count").inner_text()
            log("1개 남음" in count_text, "12. 카운터 표시", f"count='{count_text}'")
        except Exception as e:
            log(False, "12. 카운터 표시", str(e))

        # --- 13. localStorage 저장 ---
        try:
            stored = page.evaluate(
                "() => JSON.parse(localStorage.getItem('shopping-list-v1') || '[]')"
            )
            has_strawberry = any(i.get("text") == "딸기" for i in stored)
            log(has_strawberry, "13. localStorage 저장", f"저장된 아이템 수={len(stored)}")
        except Exception as e:
            log(False, "13. localStorage 저장", str(e))

        # --- 14. 새로고침 후 데이터 유지 ---
        try:
            page.reload()
            page.wait_for_load_state("domcontentloaded")
            page.wait_for_timeout(400)
            visible = page.locator(".item-text", has_text="딸기").count()
            log(visible == 1, "14. 새로고침 후 데이터 유지", f"딸기 보임={visible}")
        except Exception as e:
            log(False, "14. 새로고침 후 데이터 유지", str(e))

        browser.close()

    # --- 최종 요약 ---
    passed = sum(1 for ok, _ in results if ok)
    failed = sum(1 for ok, _ in results if not ok)
    total = len(results)
    print()
    print("=" * 45)
    print(f"  테스트 결과: {passed}/{total} 통과  |  실패: {failed}")
    print("=" * 45)
    if failed:
        print("  실패 항목:")
        for ok, name in results:
            if not ok:
                print(f"    - {name}")
    else:
        print("  모든 테스트를 통과했습니다!")
    print("=" * 45)

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    run_tests()
