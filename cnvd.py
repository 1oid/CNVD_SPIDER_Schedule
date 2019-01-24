import requests
import re
import time
import copy
import schedule
from spider.config import SCHEDULE_TASK_DAY_AT, RECEIVERS, LOOP_SLEEP
from spider.smtpSend import SmtpSender


typeid_list = {
    "29": "WebApp",
    "32": "WebProduct",
    "28": "App",
    "27": "System",
    "30": "Database",
    "31": "NetworkDevices"
}
request = requests.Session()
headers = {
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:60.0) Gecko/20100101 Firefox/60.0"
}


# 这两个用来对比数据
all = []
new_all = []


def check_list(type_id, today):
    today_list_info = []
    page = 1

    while True:
        p = (page - 1) * 20
        target = "http://www.cnvd.org.cn/flaw/typeResult?typeId={typeid}&max=20&offset={p}".format(typeid=type_id, p=p)
        # pages = re.findall(r'class="step">(\d+)</a>', r.text)[-1]
        r = requests.post(target, headers=headers)

        # 匹配
        titles = re.findall(r'<a href="(/flaw/show/CNVD-\d{4}-\d+)" title="(.*?)">', r.text)
        times = re.findall(r'<td width="13%">(\d{4}-\d{2}-\d{2})</td>', r.text)

        for index, linkInfo in enumerate(titles):
            link, title = linkInfo
            date = times[index]

            # 将今天的数据爬下来保存到list里面
            if date == today:
                today_list_info.append({"title": title, "date": date, "link": link})
            else:
                return today_list_info
        page += 1


def task():
    all = copy.copy(new_all)
    # 获取今天的数据
    t = time.localtime(time.time())
    today = "{year}-{month}-{day}".format(year=t.tm_year, month="0" + str(t.tm_mon) if t.tm_mon < 10 else t.tm_mon,
                                              day=t.tm_mday)

    with open("s.txt") as f:
        sign = f.read().strip()

    if sign != today:
        # 保存到时间和今天的时间不对等话,
        # 说明已经到了第二天, 将数组清空, 重新开始存储
        all = []
        with open("s.txt", "w") as f:
            f.write(today)

    # 迭代所有的分类板块爬虫
    for typeid, typeName in typeid_list.items():
        ret_check_data_list = check_list(typeid, today)
        print("[+] Check typeName {}, id {}, data total: {}".format(typeName, typeid, len(ret_check_data_list)))

        for data in ret_check_data_list:
            new_all.append(data.get("link"))
            # print("{}\t{}\t{}".format(data.get("title"), data.get("date"), data.get("link")))

        if len(ret_check_data_list) == 0:
            continue

        if len(set(new_all).difference(set(all))) != 0:
            message = "\n".join(["更新时间: {}\n漏洞标题: {}\n漏洞地址:http://www.cnvd.org.cn{}".format(item.get("date"),
                                                                                       item.get("title"), item.get("link"))
                                                  for item in ret_check_data_list])
            # 发信
            for receiver in RECEIVERS:
                SmtpSender("{}今日漏洞预警, 漏洞分类: {}".format(today, typeName), message, receiver)


if __name__ == '__main__':

    # 添加时间计划
    schedule_task_day_at = SCHEDULE_TASK_DAY_AT
    for day_at in schedule_task_day_at:
        print("[*] at {} put into the Schedule queue.".format(day_at))
        schedule.every().day.at(day_at).do(task)

    while True:
        schedule.run_pending()
        time.sleep(LOOP_SLEEP)