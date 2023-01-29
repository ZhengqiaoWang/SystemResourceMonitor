import glob
import os

import iMail


class MAIL(object):

    def __init__(self, args):

        # the information for enable mailing
        self.__sender = {
            'host': args.mail_server,
            'address': args.sender_addr,
            'name': args.sender_name,
            'pwd': args.pwd,
            'receivers': args.receivers,
        }

        self.__output_path = args.output  # the path of outputs
        self.__enable = args.mail  # whether the mailing system is enabled

    def send_mail(self, subject='监控统计', content='', attachments=None):
        """
        Package process monitoring results and send them to users via email
        """

        # Create an email object for iMail
        mail_system = iMail.EMAIL(host=self.__sender['host'], sender_addr=self.__sender['address'],
                                  pwd=self.__sender['pwd'], sender_name=self.__sender['name'])

        # Set the receiver list
        mail_system.set_receiver(self.__sender['receivers'])

        # New an email
        mail_system.new_mail(subject=subject, encoding='utf-8')

        # If user does not set the content,
        #   use the content of 'summary.txt';
        # Else, attach the file and sent it through email
        if content == '':
            with open(os.path.join(self.__output_path, 'summary.txt'), 'r', encoding='utf-8') as file:
                mail_system.add_text(content=file.read())
        else:
            mail_system.add_text(content=content)
            mail_system.attach_files(os.path.join(self.__output_path, 'summary.txt'))

        # Attach all output files or the specified files
        if attachments == None:
            files = glob.glob(os.path.join(self, 'process/*'))
            mail_system.attach_files(files)
        else:
            mail_system.attach_files(attachments)

        mail_system.send_mail()

    def mail(self, subject='监控统计', content='', attachments=None):

        if self.__enable:
            print("邮件发送中，请等待...")
            try:
                self.send_mail(subject, content, attachments)
                print("邮件发送成功")
            except Exception as e:
                print("邮件发送失败: {}，请自行查看".format(e))
