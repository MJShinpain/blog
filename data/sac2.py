import requests
import requests_cache
import csv
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

# Install cache with an expiration time of 2 days
requests_cache.install_cache('performance_cache', expire_after=timedelta(days=2))

def fetch_performances(url, headers, start_date, end_date):
    data = {
        "searchYear": str(start_date.year),
        "searchMonth": str(start_date.month),
        "searchFirstDay": "1",
        "searchLastDay": "31",
        "CATEGORY_PRIMARY": "2"
    }
    response = requests.post(url, data=data, headers=headers)
    return response.json()


def extract_additional_info(link):
    response = requests.get(link)
    soup = BeautifulSoup(response.content, "html.parser")
    cwa_tab = soup.find("ul", class_="cwa-tab")
    if cwa_tab:
        li_elements = cwa_tab.find_all("li")
        for index, li in enumerate(li_elements):
            if "작품소개" in li.get_text():
                ctl_sub = soup.select(f".cwa-tab-list .ctl-sub:nth-of-type({index + 1})")
                return str(ctl_sub[0]) if ctl_sub else "작품소개 not found"
    return "cwa-tab not found"


def extract_thumbnail(link):
    response = requests.get(link)
    soup = BeautifulSoup(response.content, "html.parser")
    dl_element = soup.find("dl", class_="area show-view-top clearfix")
    if dl_element:
        img_element = dl_element.find("img")
        return img_element["src"] if img_element else "No image found"
    return "dl element not found"


def main():
    url = "https://www.sac.or.kr/site/main/program/getProgramCalList"
    headers = {
        # ... (same as in the original code)
    }

    concert_hall_performances = []
    now = datetime.now()

    for i in range(12):
        start_date = now + timedelta(days=30 * i)
        end_date = start_date + timedelta(days=30)
        json_data = fetch_performances(url, headers, start_date, end_date)

        for key in json_data.keys():
            if isinstance(key, str) and key.isdigit():
                for performance in json_data[key]:
                    if performance["PLACE_NAME"] == "콘서트홀":
                        date = datetime.strptime(performance["BEGIN_DATE"], "%Y.%m.%d")
                        if date.date() >= now.date():
                            name = performance["PROGRAM_SUBJECT"]
                            time = performance["PROGRAM_PLAYTIME"]
                            sn = performance["SN"]
                            price = performance.get("PRICE_INFO", "가격 정보 없음")
                            ticket_open_date = performance.get("TICKET_OPEN_DATE", "예매 일정 없음")
                            link = f"https://www.sac.or.kr/site/main/show/show_view?SN={sn}"

                            additional_info = extract_additional_info(link)
                            thumbnail = extract_thumbnail(link)

                            concert_hall_performances.append({
                                "name": name,
                                "date": date.strftime("%Y-%m-%d"),
                                "time": time,
                                "link": link,
                                "price": price,
                                "ticket_open_date": ticket_open_date,
                                "additional_info": additional_info,
                                "thumbnail": thumbnail
                            })

    concert_hall_performances.sort(key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d'), reverse=False)

    with open("sac2.csv", "w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["name", "date", "time", "link", "price", "ticket_open_date",
                                                  "additional_info", "thumbnail"], quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(concert_hall_performances)

    print("결과가 sac2.csv 파일로 저장되었습니다.")


if __name__ == "__main__":
    main()