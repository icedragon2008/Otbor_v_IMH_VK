"""
Автоматизированный тест-кейс для https://www.demoblaze.com/
Сценарий:
  1. Открыть главную страницу
  2. Нажать на товар "Samsung galaxy s6"
  3. На странице товара нажать "Add to cart"
  4. Нажать "OK" в pop-up
  5. Нажать кнопку "Cart" в шапке сайта
Ожидаемый результат: в корзине отображается единственный элемент "Samsung galaxy s6".

Запуск: python VK-QA.py
"""

from playwright.sync_api import sync_playwright, expect


def run_test() -> bool:
    """Выполняет тест-кейс. Возвращает True, если тест пройден."""
    print("=" * 60)
    print("СТАРТ ТЕСТА: Добавление Samsung galaxy s6 в корзину")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        context = browser.new_context()
        page = context.new_page()

        try:
            # --- Шаг 1: Открыть страницу ---
            print("\n[Шаг 1] Открываем https://www.demoblaze.com/ ...")
            page.goto("https://www.demoblaze.com/", wait_until="domcontentloaded")
            page.wait_for_selector(".card-title a", timeout=15000)
            print("  ✓ Страница загружена")

            # --- Шаг 2: Нажать на товар «Samsung galaxy s6» ---
            print("\n[Шаг 2] Кликаем по товару 'Samsung galaxy s6' ...")
            page.get_by_role("link", name="Samsung galaxy s6", exact=True).click()
            page.wait_for_selector("h2.name", timeout=15000)
            product_title = page.locator("h2.name").inner_text()
            print(f"  ✓ Открыта страница товара: {product_title}")

            # --- Шаг 3 + 4: Add to cart + OK в pop-up ---
            print("\n[Шаг 3] Нажимаем 'Add to cart' ...")
            dialog_message = {}

            def handle_dialog(dialog):
                dialog_message["text"] = dialog.message
                print(f"  ✓ Получен pop-up: {dialog.message}")
                print("  ✓ Нажимаем 'OK' ...")
                dialog.accept()

            page.once("dialog", handle_dialog)

            # ВАЖНО: exact=True, чтобы кликнуть именно "Add to cart" (не "Cart")
            page.get_by_role("link", name="Add to cart", exact=True).click()

            # Ждём, пока обработчик диалога отработает
            page.wait_for_timeout(1000)

            if "text" not in dialog_message:
                raise AssertionError("Pop-up не появился после 'Add to cart'")
            if "Product added" not in dialog_message["text"]:
                raise AssertionError(
                    f"Неожиданное сообщение в pop-up: {dialog_message['text']}"
                )
            print("  ✓ Товар добавлен в корзину")

            # --- Шаг 5: Нажать «Cart» в шапке ---
            print("\n[Шаг 5] Кликаем по кнопке 'Cart' в шапке сайта ...")
            # ИСПРАВЛЕНО: exact=True, чтобы не пересекаться с "Add to cart".
            # Альтернатива: page.locator("#cartur").click()
            page.get_by_role("link", name="Cart", exact=True).click()

            page.wait_for_selector("#tbodyid tr", timeout=15000)
            print("  ✓ Корзина открыта")

            # --- Проверка ожидаемого результата ---
            print("\n[Проверка] Анализируем содержимое корзины ...")
            rows = page.locator("#tbodyid tr")
            count = rows.count()
            print(f"  Количество строк в корзине: {count}")

            if count != 1:
                raise AssertionError(
                    f"Ожидался ровно 1 товар в корзине, найдено: {count}"
                )

            first_row_text = rows.first.inner_text()
            print(f"  Содержимое строки: {first_row_text!r}")

            expect(rows.first).to_contain_text("Samsung galaxy s6")
            print("  ✓ В корзине ровно один товар 'Samsung galaxy s6'")

            print("\n" + "=" * 60)
            print("РЕЗУЛЬТАТ: ТЕСТ ПРОЙДЕН ✓")
            print("=" * 60)
            return True

        except Exception as e:
            print("\n" + "=" * 60)
            print(f"РЕЗУЛЬТАТ: ТЕСТ ПРОВАЛЕН ✗")
            print(f"Причина: {e}")
            print("=" * 60)
            try:
                page.screenshot(path="failure_screenshot.png", full_page=True)
                print("Скриншот ошибки сохранён: failure_screenshot.png")
            except Exception:
                pass
            return False

        finally:
            context.close()
            browser.close()


if __name__ == "__main__":
    success = run_test()
    raise SystemExit(0 if success else 1)