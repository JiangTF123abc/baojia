"""
邮件服务模块

提供 SMTP 邮件发送功能，支持验证码邮件模板。
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from flask import current_app


logger = logging.getLogger(__name__)


class EmailService:
    """邮件服务类
    
    负责发送各类邮件，包括验证码邮件、通知邮件等。
    使用 SMTP 协议发送邮件，支持 TLS 加密。
    """

    def __init__(self):
        """初始化邮件服务"""
        self.smtp_host = None
        self.smtp_port = None
        self.smtp_user = None
        self.smtp_password = None
        self.mail_from_address = None
        self.mail_from_name = None

    def _load_config(self):
        """从 Flask 配置中加载邮件服务器配置"""
        self.smtp_host = current_app.config.get('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = current_app.config.get('SMTP_PORT', 587)
        self.smtp_user = current_app.config.get('SMTP_USER', '')
        self.smtp_password = current_app.config.get('SMTP_PASSWORD', '')
        self.mail_from_address = current_app.config.get('MAIL_FROM_ADDRESS', self.smtp_user)
        self.mail_from_name = current_app.config.get('MAIL_FROM_NAME', '电气设备报价系统')

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        max_retries: int = 3
    ) -> bool:
        """发送邮件
        
        Args:
            to_email: 收件人邮箱地址
            subject: 邮件主题
            html_content: HTML 格式的邮件内容
            text_content: 纯文本格式的邮件内容（可选）
            max_retries: 最大重试次数，默认 3 次
            
        Returns:
            bool: 发送成功返回 True，失败返回 False
        """
        self._load_config()

        # 验证配置
        if not self.smtp_user or not self.smtp_password:
            logger.error('SMTP 配置不完整，无法发送邮件')
            return False

        # 创建邮件对象
        msg = MIMEMultipart('alternative')
        msg['From'] = f'{self.mail_from_name} <{self.mail_from_address}>'
        msg['To'] = to_email
        msg['Subject'] = subject

        # 添加纯文本内容
        if text_content:
            part1 = MIMEText(text_content, 'plain', 'utf-8')
            msg.attach(part1)

        # 添加 HTML 内容
        part2 = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(part2)

        # 尝试发送邮件（带重试机制）
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f'尝试发送邮件到 {to_email} (第 {attempt} 次)')
                
                # 连接 SMTP 服务器
                with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10) as server:
                    server.starttls()  # 启用 TLS 加密
                    server.login(self.smtp_user, self.smtp_password)
                    server.send_message(msg)
                
                logger.info(f'邮件发送成功: {to_email}')
                return True
                
            except smtplib.SMTPAuthenticationError as e:
                logger.error(f'SMTP 认证失败: {str(e)}')
                return False  # 认证失败不重试
                
            except smtplib.SMTPException as e:
                logger.warning(f'SMTP 错误 (第 {attempt} 次): {str(e)}')
                if attempt == max_retries:
                    logger.error(f'邮件发送失败，已达到最大重试次数: {to_email}')
                    return False
                    
            except Exception as e:
                logger.warning(f'发送邮件时发生错误 (第 {attempt} 次): {str(e)}')
                if attempt == max_retries:
                    logger.error(f'邮件发送失败: {to_email}')
                    return False

        return False

    def send_verification_code(self, to_email: str, code: str, purpose: str = 'password_reset') -> bool:
        """发送验证码邮件
        
        Args:
            to_email: 收件人邮箱地址
            code: 6位数字验证码
            purpose: 验证码用途，默认为 'password_reset'
            
        Returns:
            bool: 发送成功返回 True，失败返回 False
        """
        # 根据用途设置邮件主题和内容
        if purpose == 'password_reset':
            subject = '密码重置验证码 - 电气设备报价系统'
            html_content = self._get_password_reset_template(code)
            text_content = f'您的密码重置验证码是：{code}\n\n验证码有效期为 5 分钟，请尽快使用。\n\n如果这不是您的操作，请忽略此邮件。'
        else:
            subject = '验证码 - 电气设备报价系统'
            html_content = self._get_generic_verification_template(code, purpose)
            text_content = f'您的验证码是：{code}\n\n验证码有效期为 5 分钟，请尽快使用。'

        return self.send_email(to_email, subject, html_content, text_content)

    def _get_password_reset_template(self, code: str) -> str:
        """获取密码重置邮件的 HTML 模板
        
        Args:
            code: 验证码
            
        Returns:
            str: HTML 格式的邮件内容
        """
        return f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>密码重置验证码</title>
</head>
<body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f4f4f4;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f4f4f4; padding: 20px;">
        <tr>
            <td align="center">
                <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <!-- Header -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); padding: 30px; text-align: center;">
                            <h1 style="color: #ffffff; margin: 0; font-size: 24px;">密码重置验证码</h1>
                        </td>
                    </tr>
                    
                    <!-- Content -->
                    <tr>
                        <td style="padding: 40px 30px;">
                            <p style="color: #333333; font-size: 16px; line-height: 1.6; margin: 0 0 20px 0;">
                                您好，
                            </p>
                            <p style="color: #333333; font-size: 16px; line-height: 1.6; margin: 0 0 30px 0;">
                                您正在进行密码重置操作。请使用以下验证码完成验证：
                            </p>
                            
                            <!-- Verification Code -->
                            <table width="100%" cellpadding="0" cellspacing="0">
                                <tr>
                                    <td align="center" style="padding: 20px 0;">
                                        <div style="background-color: #f0f9ff; border: 2px dashed #3b82f6; border-radius: 8px; padding: 20px; display: inline-block;">
                                            <span style="font-size: 32px; font-weight: bold; color: #1d4ed8; letter-spacing: 8px; font-family: 'Courier New', monospace;">
                                                {code}
                                            </span>
                                        </div>
                                    </td>
                                </tr>
                            </table>
                            
                            <p style="color: #666666; font-size: 14px; line-height: 1.6; margin: 30px 0 0 0;">
                                <strong>重要提示：</strong>
                            </p>
                            <ul style="color: #666666; font-size: 14px; line-height: 1.8; margin: 10px 0; padding-left: 20px;">
                                <li>验证码有效期为 <strong>5 分钟</strong>，请尽快使用</li>
                                <li>请勿将验证码告知他人</li>
                                <li>如果这不是您的操作，请忽略此邮件</li>
                            </ul>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #f8f9fa; padding: 20px 30px; text-align: center; border-top: 1px solid #e5e7eb;">
                            <p style="color: #6b7280; font-size: 12px; margin: 0; line-height: 1.6;">
                                此邮件由系统自动发送，请勿直接回复。<br>
                                © 2025 电气设备报价系统 版权所有
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
'''

    def _get_generic_verification_template(self, code: str, purpose: str) -> str:
        """获取通用验证码邮件的 HTML 模板
        
        Args:
            code: 验证码
            purpose: 验证码用途
            
        Returns:
            str: HTML 格式的邮件内容
        """
        return f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>验证码</title>
</head>
<body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f4f4f4;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f4f4f4; padding: 20px;">
        <tr>
            <td align="center">
                <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <tr>
                        <td style="background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); padding: 30px; text-align: center;">
                            <h1 style="color: #ffffff; margin: 0; font-size: 24px;">验证码</h1>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 40px 30px; text-align: center;">
                            <p style="color: #333333; font-size: 16px; margin: 0 0 30px 0;">
                                您的验证码是：
                            </p>
                            <div style="background-color: #f0f9ff; border: 2px dashed #3b82f6; border-radius: 8px; padding: 20px; display: inline-block;">
                                <span style="font-size: 32px; font-weight: bold; color: #1d4ed8; letter-spacing: 8px; font-family: 'Courier New', monospace;">
                                    {code}
                                </span>
                            </div>
                            <p style="color: #666666; font-size: 14px; margin: 30px 0 0 0;">
                                验证码有效期为 5 分钟，请尽快使用。
                            </p>
                        </td>
                    </tr>
                    <tr>
                        <td style="background-color: #f8f9fa; padding: 20px 30px; text-align: center; border-top: 1px solid #e5e7eb;">
                            <p style="color: #6b7280; font-size: 12px; margin: 0;">
                                © 2025 电气设备报价系统
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
'''


# 创建全局邮件服务实例
email_service = EmailService()
