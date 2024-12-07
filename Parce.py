from flask import Flask, render_template, request
import requests
import math

app = Flask(__name__)

def fetch_vacancies(keyword, area=1, min_salary=0, page=0, per_page=20):
    url = "https://api.hh.ru/vacancies"
    headers = {
        "User-Agent": "Your User Agent",
    }
    params = {
        "text": keyword,
        "area": area,  # ID города
        "per_page": per_page,  # Количество вакансий на одной странице
        "page": page,  # Текущая страница
    }

    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        data = response.json()
        vacancies = []
        for vacancy in data.get("items", []):
            salary_info = vacancy.get("salary", {})
            if salary_info and salary_info.get("from") and salary_info.get("currency") == "RUR":
                salary = salary_info.get("from")
                if salary < min_salary:
                    continue
            elif min_salary > 0:
                continue

            vacancies.append({
                "id": vacancy.get("id"),
                "title": vacancy.get("name"),
                "url": vacancy.get("alternate_url"),
                "company": vacancy.get("employer", {}).get("name"), # Компания
                "salary": salary_info, # Зарплата
                "description": vacancy.get("snippet", {}).get("responsibility", "No description"),  # Краткое описание
                "city": vacancy.get("area", {}).get("name", "Unknown"),  # Город
            })
        return vacancies, data.get("pages", 1)  # Вакансии и общее количество страниц
    else:
        return [], 0

@app.route("/", methods=["GET", "POST"])
def index():
    vacancies = []
    total_pages = 0
    current_page = int(request.args.get("page", 1)) - 1
    per_page = 10  # Количество вакансий на странице

    # Параметры фильтрации
    keyword = request.form.get("keyword") or request.args.get("keyword", "")
    area = request.form.get("area") or request.args.get("area", "2")  # Выбор по умолчанию: Санкт-Петербург (ID = 2)
    min_salary = int(request.form.get("min_salary", request.args.get("min_salary", 30000))) # Выбор по умолчанию: мин зарплата.

    if keyword:
        vacancies, total_pages = fetch_vacancies(
            keyword=keyword,
            area=int(area),
            min_salary=min_salary,
            page=current_page,
            per_page=per_page
        )

    return render_template(
        "index.html",
        vacancies=vacancies,
        current_page=current_page + 1,
        total_pages=total_pages,
        keyword=keyword,
        area=area,
        min_salary=min_salary,
    )

if __name__ == "__main__":
   app.run(debug=False)