import tkinter as tk
from tkinter import scrolledtext
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
import threading

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

def main_loop(log_text):
    # 设置Chrome选项
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 无头模式，不打开浏览器窗口

    # 设置WebDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # 记录访问时间的字典
    visited_urls = defaultdict(float)
    email_count = 0

    while True:
        log_text.insert(tk.END, "Starting new cycle...\n")
        log_text.see(tk.END)

        # 访问目标网页
        driver.get("https://live.douyin.com/")
        log_text.insert(tk.END, "Accessed main page.\n")
        log_text.see(tk.END)

        # 等待页面加载
        time.sleep(5)
        log_text.insert(tk.END, "Page loaded.\n")
        log_text.see(tk.END)

        # 获取所有类似https://live.douyin.com/886987977322的链接
        links = driver.find_elements(By.XPATH, "//a[contains(@href, 'https://live.douyin.com/')]")
        urls = [link.get_attribute("href") for link in links if re.match(r'https://live.douyin.com/\d+', link.get_attribute("href"))]
        log_text.insert(tk.END, f"Found {len(urls)} URLs.\n")
        log_text.see(tk.END)

        # 将结果输出到根目录下的web.txt文件中
        with open("web.txt", "w") as file:
            for url in urls:
                file.write(url + "\n")
        log_text.insert(tk.END, "URLs saved to web.txt.\n")
        log_text.see(tk.END)

        # 逐个访问网站链接，时间间隔为1分钟
        for url in urls:
            if time.time() - visited_urls[url] < 3600:  # 60分钟 = 3600秒
                log_text.insert(tk.END, f"Skipping {url} as it was visited within the last 20 minutes.\n")
                log_text.see(tk.END)
                continue

            driver.get(url)
            log_text.insert(tk.END, f"Visiting {url}...\n")
            log_text.see(tk.END)
            time.sleep(6)  # 等待6秒

            # 记录访问时间
            visited_urls[url] = time.time()

            # 检查是否有指定的元素
            try:
                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@class='ZOCwtrnX']"))
                )
                log_text.insert(tk.END, f"在 {url} 中找到了指定的元素\n")
                log_text.see(tk.END)
                send_email(url)
                email_count += 1
                log_text.insert(tk.END, f"Email sent. Total emails sent: {email_count}\n")
                log_text.see(tk.END)
            except TimeoutException:
                log_text.insert(tk.END, f"在 {url} 中没有找到指定的元素\n")
                log_text.see(tk.END)

        log_text.insert(tk.END, "Cycle completed. Waiting for next cycle...\n")
        log_text.see(tk.END)
        time.sleep(60)  # 每分钟检查一次

# 创建GUI界面
root = tk.Tk()
root.title("Douyin Live Monitor")

frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

log_text = scrolledtext.ScrolledText(frame, width=80, height=20)
log_text.pack(padx=10, pady=10)

start_button = tk.Button(frame, text="Start Monitoring", command=lambda: threading.Thread(target=main_loop, args=(log_text,)).start())
start_button.pack(padx=10, pady=10)

root.mainloop()
