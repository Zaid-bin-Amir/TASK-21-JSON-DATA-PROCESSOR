import json
import sys

INPUT_FILE = "employees.json"
OUTPUT_FILE = "results.json"
REQUIRED_KEYS = {"id", "name", "department", "salary", "active", "skills", "address"}


def load_data(path):
    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        print(f"Error: file '{path}' not found.")
        sys.exit(1)
    except json.JSONDecodeError as error:
        print(f"Error: invalid JSON format ({error}).")
        sys.exit(1)

    if "employees" not in data or not isinstance(data["employees"], list):
        print("Error: key 'employees' missing or not a list.")
        sys.exit(1)

    return data


def validate_employees(employees):
    valid = []
    for employee in employees:
        missing = REQUIRED_KEYS - employee.keys()
        if missing:
            print(f"Skipping record {employee.get('id', '?')}: missing {sorted(missing)}")
            continue
        valid.append(employee)
    return valid


def search_by_name(employees, keyword):
    keyword = keyword.lower()
    return [e for e in employees if keyword in e["name"].lower()]


def filter_by_department(employees, department):
    return [e for e in employees if e["department"].lower() == department.lower()]


def filter_by_min_salary(employees, minimum):
    return [e for e in employees if e["salary"] >= minimum]


def filter_by_skill(employees, skill):
    return [e for e in employees if skill.lower() in (s.lower() for s in e["skills"])]


def filter_by_city(employees, city):
    return [e for e in employees if e["address"].get("city", "").lower() == city.lower()]


def filter_active(employees):
    return [e for e in employees if e["active"]]


def summarize(employees):
    if not employees:
        return {"total_employees": 0}

    salaries = [e["salary"] for e in employees]
    highest = max(employees, key=lambda e: e["salary"])
    lowest = min(employees, key=lambda e: e["salary"])

    departments = {}
    for employee in employees:
        info = departments.setdefault(employee["department"], {"count": 0, "total_salary": 0})
        info["count"] += 1
        info["total_salary"] += employee["salary"]

    for info in departments.values():
        info["average_salary"] = round(info["total_salary"] / info["count"], 2)

    return {
        "total_employees": len(employees),
        "active_employees": len(filter_active(employees)),
        "inactive_employees": len(employees) - len(filter_active(employees)),
        "total_salary": sum(salaries),
        "average_salary": round(sum(salaries) / len(salaries), 2),
        "highest_paid": {"name": highest["name"], "salary": highest["salary"]},
        "lowest_paid": {"name": lowest["name"], "salary": lowest["salary"]},
        "departments": departments,
    }


def print_employees(title, employees):
    print(f"\n=== {title} ({len(employees)} found) ===")
    if not employees:
        print("No records found.")
        return
    print(f"{'ID':<6}{'Name':<18}{'Department':<18}{'Salary':>10}  City")
    print("-" * 66)
    for e in employees:
        print(f"{e['id']:<6}{e['name']:<18}{e['department']:<18}{e['salary']:>10}  {e['address']['city']}")


def print_summary(summary):
    print("\n=== Summary Report ===")
    print(f"Total employees   : {summary['total_employees']}")
    print(f"Active / Inactive : {summary['active_employees']} / {summary['inactive_employees']}")
    print(f"Total salary      : {summary['total_salary']}")
    print(f"Average salary    : {summary['average_salary']}")
    print(f"Highest paid      : {summary['highest_paid']['name']} ({summary['highest_paid']['salary']})")
    print(f"Lowest paid       : {summary['lowest_paid']['name']} ({summary['lowest_paid']['salary']})")
    print("\nDepartment-wise:")
    for name, info in summary["departments"].items():
        print(f"  {name:<18} count={info['count']}  avg_salary={info['average_salary']}")


def save_results(path, results):
    with open(path, "w", encoding="utf-8") as file:
        json.dump(results, file, indent=4)
    print(f"\nResults saved to '{path}'.")


def main():
    data = load_data(INPUT_FILE)
    employees = validate_employees(data["employees"])
    print(f"Company: {data.get('company', 'Unknown')}")
    print(f"Valid records loaded: {len(employees)}")

    searched = search_by_name(employees, "sara")
    engineering = filter_by_department(employees, "Engineering")
    high_salary = filter_by_min_salary(employees, 100000)
    sql_skilled = filter_by_skill(employees, "SQL")
    lahore_staff = filter_by_city(employees, "Lahore")
    active_staff = filter_active(employees)

    print_employees("Search: name contains 'sara'", searched)
    print_employees("Filter: Engineering department", engineering)
    print_employees("Filter: salary >= 100000", high_salary)
    print_employees("Filter: skill = SQL", sql_skilled)
    print_employees("Filter: city = Lahore", lahore_staff)

    print_employees("Filter: active employees only", active_staff)

    summary = summarize(employees)
    print_summary(summary)

    results = {
        "search_name_sara": searched,
        "engineering_department": engineering,
        "salary_100000_or_more": high_salary,
        "skill_sql": sql_skilled,
        "city_lahore": lahore_staff,
        "active_employees": active_staff,
        "summary": summary,
    }
    save_results(OUTPUT_FILE, results)


if __name__ == "__main__":
    main()
