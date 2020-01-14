import os
from datetime import date, datetime

import requests
from requests.adapters import HTTPAdapter

from goldminer.common.FinancialReportType import FinancialReportType
from goldminer.common.HttpUtil import HttpUtil
from goldminer.common.logger import get_logger
from goldminer.models.models import CnInfoOrgId
from goldminer.storage.CnInfoOrgIdDao import CnInfoOrgIdDao


class FinancialReportCrawler:
    """
    Debug at:
    http://www.cninfo.com.cn/new/commonUrl/pageOfSearch?url=disclosure/list/search&checkedCategory=category_ndbg_szsh#
    """

    def __init__(self):
        self._headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en-GB,en;q=0.9,en-US;q=0.8,zh-CN;q=0.7,zh;q=0.6",
            "Host": "www.cninfo.com.cn",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Referer": "http://www.cninfo.com.cn/new/commonUrl?url=disclosure/list/notice",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36",
            "Origin": "http://www.cninfo.com.cn",
            'column': 'szse',
            "X-Requested-With": "XMLHttpRequest",
            'plate': 'sz',
        }
        self._base_url = "http://www.cninfo.com.cn/new/hisAnnouncement/query"
        self._pdf_base_url = "http://static.cninfo.com.cn/"
        self._stock_list_url = "http://www.cninfo.com.cn/new/data/szse_stock.json"

        self.cnInfoOrgIdDao = CnInfoOrgIdDao()
        self.__logger = get_logger(__name__)

        self.output_path = "/Users/abing/Documents/财报/"

    def get_headers(self):
        headers = self._headers
        headers['User-Agent'] = HttpUtil.random_user_agent()
        return headers

    def call_cninfo_js_api(self, url, headers, params=None, method='post'):
        """
        Call eastmoney api to get forecast messages
        :param url:
        :param headers:
        :param params:
        :return:
        tuple (
        )
        """

        session = requests.Session()
        session.mount('http://', HTTPAdapter(max_retries=2))
        session.mount('https://', HTTPAdapter(max_retries=2))

        if method == 'post':
            response = session.post(url, data=params, json=None, headers=headers)
        else:
            response = session.get(url, params=params, headers=headers)

        if not response or response.status_code != 200 or not response.text or response.text == "":
            self.__logger.error("Failed to download data from url={}, params={}".format(url, params))
            return None
        return response

    def download_announcements(self, url, headers, params, max_page=3):
        result = []
        while max_page > 0:
            response = self.call_cninfo_js_api(url, headers, params)
            if not response:
                self.__logger.error("Failed to download data from url={}, params={}".format(url, params))
                break
            response = response.json()

            result.extend(response['announcements'])
            if not response['hasMore']:
                break

            response['pageNum'] += 1
            max_page -= 1

        return result

    def parse_title(self, title):
        year = title[:4]
        if title.find("一季度") >= 0:
            type = FinancialReportType.FirstQuarter
        elif title.find("半年度") >= 0:
            type = FinancialReportType.SemiAnnual
        elif title.find("三季度") >= 0:
            type = FinancialReportType.ThirdQuarter
        elif title.find("年度") >= 0:
            type = FinancialReportType.Annual
        else:
            raise Exception("Failed to extract report type from title {}".format(title))
        return year, type

    def download_announcement(self, code, announcement, output_path):
        """

        :param code:
        :param announcement: {"id":null,"secCode":"000001","secName":"平安银行","orgId":"gssz0000001","announcementId":"1206997843","announcementTitle":"2019年第三季度报告全文","announcementTime":1571673600000,"adjunctUrl":"finalpage/2019-10-22/1206997843.PDF","adjunctSize":849,"adjunctType":"PDF","storageTime":null,"columnId":null,"pageColumn":null,"announcementType":"01010503||010112||01030701","associateAnnouncement":null,"important":null,"batchNum":null,"announcementContent":null,"orgName":null,"announcementTypeName":null}
        :param output_path:
        :return:
        """
        year, type = self.parse_title(announcement['announcementTitle'])

        folder = os.path.join(output_path, announcement['secCode'], year)
        if not os.path.exists(folder):
            os.makedirs(folder)

        output_file = folder + os.path.sep + str(type.value) + ".pdf"
        url = self._pdf_base_url + announcement['adjunctUrl']

        self.download_file(url, output_file)

    def download_file(self, url, output_file):
        response = requests.get(url, stream=True, verify=False)
        total_size = int(response.headers['Content-Length'])

        if os.path.exists(output_file):
            temp_size = os.path.getsize(output_file)  # 本地已经下载的文件大小
        else:
            temp_size = 0

        if temp_size >= total_size:
            self.__logger.info("{} is already downloaded.".format(output_file))
            return

        self.__logger.info(
            "start to download {} from url {}\ntotal size={}, start size={}" \
                .format(output_file, url, total_size, temp_size))

        headers = {'Range': 'bytes=%d-' % temp_size}
        response = requests.get(url, stream=True, verify=False, headers=headers)
        with open(output_file, "ab") as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    temp_size += len(chunk)
                    f.write(chunk)
                    f.flush()

    def get_announcements_by_code(self, code, start_date: date, end_date: date):
        stock = "{},{}".format(code, self.get_org_id(code))
        se_date = "{}~{}".format(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))

        params = {
            'stock': stock,
            'searchkey': '',
            'category': 'category_ndbg_szsh;category_bndbg_szsh;category_yjdbg_szsh;category_sjdbg_szsh',
            'trade': '',
            'pageNum': 1,
            'pageSize': 30,
            'tabName': 'fulltext',
            'seDate': se_date,
            'isHLtitle': 'true',
            'secid': '',
            'plate': '',
            'column': 'szse',
            'sortName': '',
            'sortTyp': '',
        }
        announcements = self.download_announcements(self._base_url, self.get_headers(), params)
        self.__logger.info("Download {} announcements for code {}".format(len(announcements), code))
        for announcement in announcements:
            if announcement['announcementTitle'].find("摘要") >= 0:
                continue
            if announcement['announcementTitle'].find("取消") >= 0:
                continue
            self.download_announcement(code, announcement, self.output_path)

    def download_and_update_org_ids(self):
        """
        Download orgId from www.cninfo.com.cn and save to
        :return:
        """

        data = self.call_cninfo_js_api(self._stock_list_url, self.get_headers(), params=None, method='get')

        for data in data["stockList"]:
            model = CnInfoOrgId()
            model.code = data['code']
            model.org_id = data['orgId']
            self.cnInfoOrgIdDao.insertOrReplace(model)
            self.__logger.info("Save orgId: {}".format(model))

    def get_org_id(self, code):
        model = self.cnInfoOrgIdDao.getByCode(code)
        if model is not None:
            return model.org_id
        else:
            raise Exception("No cninfo org id found for code {}, "
                            "please run FinancialReportDownloader.download_and_update_org_ids to update it".format(
                code))


if __name__ == "__main__":
    crawler = FinancialReportCrawler()
    crawler.get_announcements_by_code('300357', datetime(2018, 1, 1).date(), datetime(2020, 1, 1).date())
    # crawler.download_and_update_org_ids()
