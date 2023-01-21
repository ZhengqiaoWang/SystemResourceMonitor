# -*- coding: UTF-8 -*-

import argparse
import os
import shutil
import signal

from SRM import monitor


# 设定信号捕获
def onSignalInterHandler(signum, frame):
    global is_running_flag
    print("Stopping...")
    print("Data handling in progress, please wait for a while...")
    is_running_flag = False


def send_mail(mail_server, sender_addr, pwd, receivers, output, sender_name='no_reply', subject='监控统计', content=''):
    """
    Package process monitoring results and send them to users via email
    """
    import iMail, glob

    # Create an email object for iMail
    mail = iMail.EMAIL(host=mail_server, sender_addr=sender_addr, pwd=pwd, sender_name=sender_name)

    # Set the receiver list
    mail.set_receiver(receivers)

    # New an email
    mail.new_mail(subject=subject, encoding='utf-8')

    # If user does not set the content,
    #   use the content of 'summary.txt';
    # Else, attach the file and sent it through email
    if content == '':
        with open(os.path.join(output, 'summary.txt'), 'r', encoding='utf-8') as file:
            mail.add_text(content=file.read())
    else:
        mail.add_text(content=content)
        mail.attach_files(os.path.join(output, 'summary.txt'))

    # Attach all output files
    files = glob.glob(os.path.join(output, 'process/*'))
    mail.attach_files(files)

    mail.send_mail()


if __name__ == '__main__':

    argparser = argparse.ArgumentParser()
    argparser.add_argument("-o", "--output", type=str,
                           help="输出位置", required=False, default="./output")
    argparser.add_argument("-i", "--interval", type=int,
                           help="监听时间间隔(毫秒)", required=False, default=5000)
    argparser.add_argument("-f", "--filter", nargs='*',
                           help="限制监听范围，为进程名(如explorer.exe)", default=[])
    argparser.add_argument("-m", "--mail", type=bool,
                           help="是否发送邮件通知", default=False)

    args = argparser.parse_args()

    shutil.rmtree(args.output, ignore_errors=True)

    # 输出系统信息
    monitor.showSystemInfo()
    # 启动监听
    sys_monitor = monitor.SysMonitor()
    is_running_flag = True

    signal.signal(signal.SIGINT, onSignalInterHandler)

    # 开启监听线程（fake线程）
    sys_monitor.start(args.interval, args.filter)
    print("\n正在监听... 键盘敲击[CTRL+C]即可结束监听并进行统计...")
    while is_running_flag:
        import time

        time.sleep(1)

    sys_monitor.stop()
    print("监听已停止...正在导出数据...")
    sys_monitor.export(args.output)

    print("结果输出到：", os.path.abspath(args.output))

    if args.mail:
        print("邮件发送中，请等待...")
        try:
            send_mail('HOST', 'SENDER_MAIL', 'PASSWORD', 'RECEIVERS', args.output)
            print("邮件发送成功")
        except:
            print("邮件发送失败，请自行查看")
