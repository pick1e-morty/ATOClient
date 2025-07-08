# coding: utf-8
import re

import requests
from PyQt5.QtCore import QVersionNumber

from app.utils.global_var import VERSION


class VersionManager:
    """Version manager"""

    def __init__(self, ignoreVersion):
        self.currentVersion = VERSION
        self.versionPattern = re.compile(r"v(\d+)\.(\d+)\.(\d+)")
        self.ignoreVersion = ignoreVersion

        self.lastestVersion = VERSION
        self.updateReleaseTitle = ""  # 更新的版本标题
        self.updateReleaseInfo = ""  # 更新的版本信息

    def getUpdateReleaseInfo(self):
        return self.lastestVersion, self.updateReleaseTitle, self.updateReleaseInfo

    def getLatestVersionMethod(self):
        """获取最新版本"""
        url = "https://gitee.com/api/v5/repos/picklemorty/ATOClient/releases/latest"
        response = requests.get(url, timeout=2)
        response.raise_for_status()

        # parse version
        response.encoding = "utf-8"
        response_json = response.json()
        self.updateReleaseTitle = response_json["name"]
        self.updateReleaseInfo = response_json["body"]
        version = response_json["tag_name"]  # type:str #  v0.0.0
        match = self.versionPattern.search(version)  # 防止代码仓库那边改变了版本的格式
        if not match:
            return VERSION  # 如果没找到就返回当前版本

        self.lastestVersion = version
        return version

    def hasNewVersion(self):
        """
        检查是否存在新版本
        如果存在新版本，返回True
        """
        self.newVersion = self.getLatestVersionMethod()
        remoteVersion, _suffixIndex = QVersionNumber.fromString(
            self.newVersion[1:]
        )  # 这个[1:]是在过滤版本号中的那个v字符
        localVersion, _suffixIndex = QVersionNumber.fromString(self.currentVersion[1:])
        ignoreVersion, _suffixIndex = QVersionNumber.fromString(self.ignoreVersion[1:])

        if remoteVersion == ignoreVersion:
            # 远程仓库版本等于要忽略的版本，没有新版本
            return False
        if localVersion >= remoteVersion:
            # 本地版本大于等于远程版本号，说明本地版本是最新的
            return False

        return True


if __name__ == "__main__":
    vm = VersionManager(ignoreVersion="v0.0.0")
    print(vm.hasNewVersion())
