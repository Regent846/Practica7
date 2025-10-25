from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import pytest
import os
import time


class TestTodoApp:
    @pytest.fixture(autouse=True)
    def setup(self):
        # Настройка Chrome options для GitHub Actions
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Обязательно для CI
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")

        # Используем ChromeDriver без user-data-dir чтобы избежать конфликтов
        self.driver = webdriver.Chrome(options=chrome_options)
        html_path = os.path.abspath("ToDoList.html") # Абсолютный путь к HTML файлу
        self.driver.get(f"file://{html_path}")
        self.wait = WebDriverWait(self.driver, 10)
        yield
        self.driver.quit()

    def test_add_task(self):
        # Тест добавления новой задачи
        # Находим элементы
        input_field = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "input")))
        add_button = self.driver.find_element(By.TAG_NAME, "button")

        # Добавляем задачу
        task_text = "Тестовая задача 1"
        input_field.send_keys(task_text)
        add_button.click()

        # Проверяем, что задача добавилась
        task_element = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "task")))
        assert task_text in task_element.text
        assert len(self.driver.find_elements(By.CLASS_NAME, "todo")) == 1

    def test_add_empty_task(self):
        # Тест попытки добавления пустой задачи
        input_field = self.driver.find_element(By.TAG_NAME, "input")
        add_button = self.driver.find_element(By.TAG_NAME, "button")

        # Пытаемся добавить пустую задачу
        input_field.send_keys("")
        add_button.click()

        # Проверяем, что alert появился
        try:
            WebDriverWait(self.driver, 3).until(EC.alert_is_present())
            alert = self.driver.switch_to.alert
            alert.accept()
            # Убеждаемся, что задачи не добавились
            tasks = self.driver.find_elements(By.CLASS_NAME, "todo")
            assert len(tasks) == 0
        except:
            pytest.fail("Alert не появился при добавлении пустой задачи")

    def test_delete_task(self):
        # Тест удаления задачи
        # Сначала добавляем задачу
        input_field = self.driver.find_element(By.TAG_NAME, "input")
        add_button = self.driver.find_element(By.TAG_NAME, "button")

        input_field.send_keys("Задача для удаления")
        add_button.click()

        # Убеждаемся, что задача добавилась
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "todo")))

        # Удаляем задачу
        delete_button = self.driver.find_element(By.CLASS_NAME, "delete")
        delete_button.click()

        # Проверяем, что задача удалилась
        self.wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "todo")))
        tasks = self.driver.find_elements(By.CLASS_NAME, "todo")
        assert len(tasks) == 0

    def test_edit_task(self):
        # Тест редактирования задачи
        # Добавляем задачу
        input_field = self.driver.find_element(By.TAG_NAME, "input")
        add_button = self.driver.find_element(By.TAG_NAME, "button")

        input_field.send_keys("Исходная задача")
        add_button.click()

        # Находим кнопку редактирования и кликаем
        edit_button = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "edit")))
        edit_button.click()

        # Редактируем текст задачи
        task_element = self.driver.find_element(By.CLASS_NAME, "task")
        task_element.clear()
        task_element.send_keys("Отредактированная задача")

        # Сохраняем изменения
        save_button = self.driver.find_element(By.CLASS_NAME, "edit")
        save_button.click()

        # Проверяем, что текст изменился
        assert "Отредактированная задача" in task_element.text

    def test_multiple_tasks(self):
        # Тест добавления нескольких задач
        input_field = self.driver.find_element(By.TAG_NAME, "input")
        add_button = self.driver.find_element(By.TAG_NAME, "button")

        # Добавляем 3 задачи
        tasks_to_add = ["Задача 1", "Задача 2", "Задача 3"]
        for task_text in tasks_to_add:
            input_field.send_keys(task_text)
            add_button.click()
            time.sleep(0.5)  # Небольшая задержка между добавлениями

        # Проверяем, что все задачи добавились
        task_elements = self.driver.find_elements(By.CLASS_NAME, "task")
        assert len(task_elements) == 3

        # Проверяем тексты задач
        task_texts = [element.text for element in task_elements]
        for task_text in tasks_to_add:
            assert task_text in task_texts

    def test_local_storage_persistence(self):
        # Тест сохранения задач в Local Storage
        # Добавляем задачу
        input_field = self.driver.find_element(By.TAG_NAME, "input")
        add_button = self.driver.find_element(By.TAG_NAME, "button")

        task_text = "Задача для проверки persistence"
        input_field.send_keys(task_text)
        add_button.click()

        # Обновляем страницу
        self.driver.refresh()

        # Проверяем, что задача сохранилась после обновления
        task_element = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "task")))
        assert task_text in task_element.text


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--html=report.html"])