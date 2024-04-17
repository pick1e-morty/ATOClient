from app.download_video_widget.netsdk.dahua_async_download import dahuaDownloader
from app.download_video_widget.netsdk.haikang_async_download import HaikangDownloader


class DownloaderFactory:
    @staticmethod
    def create_product(product_type):
        if product_type == "dahua":
            return dahuaDownloader
        elif product_type == "haikang":
            return HaikangDownloader
        else:
            raise ValueError("非法设备类型")
