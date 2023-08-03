import os
import time
import smtplib
import schedule
import subprocess
from email.mime.text import MIMEText
from email.header import Header
import logging
import logging.handlers

# 邮件配置
smtp_server = 'smtp.qq.com'  # SMTP服务器地址
smtp_port = 465  # SMTP服务器端口号（SSL加密）
smtp_user = '2111256206@qq.com'  # 发件人邮箱
smtp_password = 'ucuacvhzxkfnbeff'  # 发件人邮箱密码
recipient = '1806986661@qq.com'  # 收件人邮箱
subject = 'GPU Notification'  # 邮件主题
content_template = 'The GPU-%d is available now.'  # 邮件正文模板

# GPU配置
gpu_count = 6  # GPU数量
query_interval = 3600  # 查询间隔（秒）
free_gpu_index = 5  # 空闲GPU索引（从0开始）

# 日志配置
log_file = f'gpu_{free_gpu_index}.log'
logging.basicConfig(
                    filename=log_file,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO
                    )
# 每天清理一次日志文件
logging_handler = logging.handlers.TimedRotatingFileHandler(filename=log_file, when='D', backupCount=1)
logging_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logging.root.handlers = [logging_handler]

def check_gpu():
    # 获取GPU使用情况
    res = subprocess.run(["nvidia-smi", "--query-gpu=utilization.gpu", "--format=csv"], capture_output=True, text=True)
    gpu_utilizations = [int(x.strip().split(" ")[0]) for x in res.stdout.strip().split("\n")[1:]]
    free_gpus = [i for i, x in enumerate(gpu_utilizations) if x == 0]
    
    # 判断第五块GPU是否空闲
    if free_gpu_index in free_gpus:
        # 发送邮件通知
        content = content_template % (free_gpu_index)
        message = MIMEText(content, 'plain', 'utf-8')
        message['From'] = smtp_user
        message['To'] = recipient
        message['Subject'] = Header(subject, 'utf-8')
        try:
            smtp = smtplib.SMTP_SSL(smtp_server, smtp_port)
            smtp.login(smtp_user, smtp_password)
            smtp.sendmail(smtp_user, recipient, message.as_string())
            smtp.quit()
            logging.info(content+' 邮件发送成功')
        except smtplib.SMTPException as e:
            # 输出异常信息
            logging.error('邮件发送失败：%s' % e)
    else:
        logging.info('The GPU-%d is busy.' % (free_gpu_index))

# 设置定时任务，每小时执行一次
schedule.every(10).minutes.do(check_gpu)

# 运行调度器
while True:
    schedule.run_pending()
