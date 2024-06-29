from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import time
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from collections import defaultdict

def send_email(url):
    # 邮件配置
    smtp_server = 'smtp.qq.com'  #发送邮件的SMTP服务器
    smtp_port = 587
    sender_email = '****@qq.com' #发送邮件的账号
    sender_password = '*****' #发送邮件账号的密码
    receiver_email = '****@qq.com'  #接收邮件的账号

    # 创建邮件
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = 'Element Found on Douyin Live'
    body = f'The element was found on the following URL: {url}'
    message.attach(MIMEText(body, 'plain'))

    # 发送邮件
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        print(f"Email sent to {receiver_email} with URL: {url}")

# 设置Chrome选项
chrome_options = Options()
chrome_options.add_argument("--headless")  # 无头模式，不打开浏览器窗口

# 设置WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# 记录访问时间的字典
visited_urls = defaultdict(float)

while True:
    # 访问目标网页
    driver.get("https://live.douyin.com/")

    # 等待页面加载
    time.sleep(5)

    # 获取所有类似https://live.douyin.com/886987977322的链接
    links = driver.find_elements(By.XPATH, "//a[contains(@href, 'https://live.douyin.com/')]")
    urls = [link.get_attribute("href") for link in links if re.match(r'https://live.douyin.com/\d+, link.get_attribute("href"))]

    # 将结果输出到根目录下的web.txt文件中
    with open("web.txt", "w") as file:
        for url in urls:
            file.write(url + "\n")

    # 逐个访问网站链接，时间间隔为1分钟
    for url in urls:
        if time.time() - visited_urls[url] < 3600:  # 60分钟 = 3600秒
            print(f"Skipping {url} as it was visited within the last 20 minutes.")
            continue

        driver.get(url)
        print(f"Visiting {url}...")
        time.sleep(6)  # 等待6秒

        # 记录访问时间
        visited_urls[url] = time.time()

        # 检查是否有指定的元素
        try:
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@class='ZOCwtrnX']"))
            )
            print(f"在 {url} 中找到了指定的元素")
            send_email(url)
        except TimeoutException:
            print(f"在 {url} 中没有找到指定的元素")

# 关闭WebDriver
driver.quit()
