# coding: UTF-8
import hashlib
import zipfile
import time

import pandas as pd
import requests
import threading
import sys
import os
from retry import retry
from queue import Queue


#########################
# 读取通达信专业财务数据
######################

class TDXFinance:
    tdxCwPath = ""
    fileType = ".pkl"
    subjectsPath = "investment/tdxSubjects.csv"
    fileInfoColumns = ['filename', 'md5', 'filesize']


    def __init__(self, cwPath, fileType, subjectsPath="investment/tdxSubjects.csv"):
        self.tdxCwPath = cwPath
        self.fileType = fileType
        self.subjectsPath = subjectsPath

    def read_cat(self):
        df = pd.read_csv('tdxSubjectCat.csv', header=0)
        return df

    def read_subjects(self, cat=0):
        subjects = pd.read_csv(self.subjectsPath, sep='--', header=0, encoding="UTF-8", engine='python')
        if cat > 0:  # 只返回指定的分类科目
            return subjects.loc[subjects['cat'] == cat]
        return subjects

    # 根据代码 @param code example:600019
    # 日期 @param date example:202209030 一般为每季的最后一天
    def get_all_infos(self, date, code):
        df = self.get_all_finance(date)
        return df.loc[df[0] == code]

    # 根据代码 @param code example:600019
    # 日期 @param date example:202209030 一般为每季的最后一天
    # 科目 @param subject (1~580) @see read_subject()
    def get_info_by_subject(self, code, date, *subject):
        pass

    # 获取指定日期的所有公司财务数据
    # 日期 @param date YYYY0331,YYYY0930,YYYY1231
    def get_all_finance(self, date):
        pkl_path=self.tdxCwPath + os.sep + 'gpcw' + date + self.fileType
        dat_path=self.tdxCwPath+os.sep+'gpcw'+date+".dat"
        pkl_size=os.stat(pkl_path).st_size
        dat_size=os.stat(dat_path).st_size
        if pkl_size<dat_size:
            df=historyfinancialreader(dat_path)
            df.to_pickle(pkl_path,compression=None)
        df = pd.read_pickle(self.tdxCwPath + os.sep + 'gpcw' + date + self.fileType)
        return df

    # 通过对比服务端和本地的列表文件查检需要更新的财务数据文件
    # 逻辑为第一步下载服务器上的列表文件，与本地比较MD5多出的或不等的就下载
    # 下载完后更新文件下载列表，如果强制更新则不比较对服务器上的文件进行全量下载。
    # increment增强更新
    # resume恢复更新失败的文件，检查文件大小与文件例表中的大小，如果不等则进行更新。
    def update(self, increment=True, resume=False):
        local_info_path=self.tdxCwPath + os.sep + "gpcw.txt"
        localListInfos = pd.read_csv(local_info_path)
        localListInfos.columns = self.fileInfoColumns
        print(localListInfos)
        localAllFileList = os.listdir(self.tdxCwPath)

        localZipFileList = []
        for file in localAllFileList:
            if len(file) == 16 and file[:4] == "gpcw" and file[-4:] == ".zip":
                localZipFileList.append(file)

        print(localZipFileList)

        self.many_thread_download = ManyThreadDownload()

        # 本地信息列表中文件名不存在于本地zip文件列表中的需直接下载
        for filename in localListInfos['filename'].tolist():
            if filename not in localZipFileList:
                self.donwload(filename)
                localZipFileList.append(filename)

        remoteFileInfo = self.load_remote_cw_info_file()
        # 远程信息列表中MD5值在本地不存在的需要下载
        remote_md5_list=remoteFileInfo['md5'].tolist()
        for filename in localZipFileList:
            local_zipfile_path=self.tdxCwPath+os.sep+filename
            file_size=os.stat(local_zipfile_path).st_size
            #with open(local_zipfile_path, 'rb') as fobj:  # 读取本机zip文件，计算md5
            #    file_content = fobj.read()
            #    file_md5 = hashlib.md5(file_content).hexdigest()
            remote_size=remoteFileInfo.loc[remoteFileInfo['filename']==filename]['filesize']
            if file_size < int(remote_size):
                print('willupdate:::'+filename)
                self.donwload(filename)

        for filename in remoteFileInfo['filename']:
            if filename not in localZipFileList:
                print('will download::::'+filename)
                self.donwload(filename)


        # 将远程文件信息更新到本地

        remoteFileInfo.to_csv(local_info_path,header=False,index=False)


    #根据文件名下载财务文件包
    def donwload(self,filename):
        tdx_zipfile_url = 'http://down.tdx.com.cn:8001/tdxfin/' + filename
        local_zipfile_path = self.tdxCwPath + os.sep + filename
        print(tdx_zipfile_url)
        print(local_zipfile_path)
        self.many_thread_download.run(tdx_zipfile_url, local_zipfile_path)
        with zipfile.ZipFile(local_zipfile_path, 'r') as zipobj:  # 打开zip对象，释放zip文件。会自动覆盖原文件。
            zipobj.extractall(self.tdxCwPath)
        local_datfile_path = local_zipfile_path[:-4] + ".dat"
        df = historyfinancialreader(local_datfile_path)
        csvpath = self.tdxCwPath +os.sep+ filename[:-4] + ".pkl"
        df.to_pickle(csvpath, compression=None)

    def load_remote_cw_info_file(self):
        tdx_txt_url = 'http://down.tdx.com.cn:8001/tdxfin/gpcw.txt'
        tdx_txt_df = self.dowload_url(tdx_txt_url)  # 下载gpcw.txt
        tdx_txt_df = tdx_txt_df.text.strip().split('\r\n')  # 分割行
        tdx_txt_df = [l.strip().split(",") for l in tdx_txt_df]  # 用,分割，二维列表
        tdx_txt_df = pd.DataFrame(tdx_txt_df, columns=self.fileInfoColumns)  # 转为df格式，好比较
        return tdx_txt_df

    @retry(tries=3, delay=3)  # 无限重试装饰性函数
    def dowload_url(self, url):
        """
        :param url:要下载的url
        :return: request.get实例化对象
        """
        import requests
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/87.0.4280.141',
        }
        response_obj = requests.get(url, headers=header, timeout=5)  # get方式请求
        response_obj.raise_for_status()  # 检测异常方法。如有异常则抛出，触发retry
        # print(f'{url} 下载完成')
        return response_obj


def historyfinancialreader(filepath):
    """
    读取解析通达信目录的历史财务数据
    :param filepath: 字符串类型。传入文件路径
    :return: DataFrame格式。返回解析出的财务文件内容
    """
    import struct

    cw_file = open(filepath, 'rb')
    header_pack_format = '<1hI1H3L'
    header_size = struct.calcsize(header_pack_format)
    stock_item_size = struct.calcsize("<6s1c1L")
    data_header = cw_file.read(header_size)
    stock_header = struct.unpack(header_pack_format, data_header)
    max_count = stock_header[2]
    report_date = stock_header[1]
    report_size = stock_header[4]
    report_fields_count = int(report_size / 4)
    report_pack_format = '<{}f'.format(report_fields_count)
    results = []
    for stock_idx in range(0, max_count):
        cw_file.seek(header_size + stock_idx * struct.calcsize("<6s1c1L"))
        si = cw_file.read(stock_item_size)
        stock_item = struct.unpack("<6s1c1L", si)
        code = stock_item[0].decode("utf-8")
        foa = stock_item[2]
        cw_file.seek(foa)
        info_data = cw_file.read(struct.calcsize(report_pack_format))
        data_size = len(info_data)
        cw_info = list(struct.unpack(report_pack_format, info_data))
        cw_info.insert(0, code)
        results.append(cw_info)
    df = pd.DataFrame(results)
    return df


class ManyThreadDownload:
    def __init__(self, num=10):
        self.num = num  # 线程数,默认10
        self.url = ''  # url
        self.name = ''  # 目标地址
        self.total = 0  # 文件大小

    # 获取每个线程下载的区间
    def get_range(self):
        ranges = []
        offset = int(self.total / self.num)
        for i in range(self.num):
            if i == self.num - 1:
                ranges.append((i * offset, ''))
            else:
                ranges.append(((i * offset), (i + 1) * offset - 1))
        return ranges  # [(0,99),(100,199),(200,"")]

    # 通过传入开始和结束位置来下载文件
    def download(self, ts_queue):
        while not ts_queue.empty():
            start_, end_ = ts_queue.get()
            headers = {
                'Range': 'Bytes=%s-%s' % (start_, end_),
                'Accept-Encoding': '*'
            }
            flag = False
            while not flag:
                try:
                    # 设置重连次数
                    requests.adapters.DEFAULT_RETRIES = 10
                    # s = requests.session()            # 每次都会发起一次TCP握手,性能降低，还可能因发起多个连接而被拒绝
                    # # 设置连接活跃状态为False
                    # s.keep_alive = False
                    # 默认stream=false,立即下载放到内存,文件过大会内存不足,大文件时用True需改一下码子
                    res = requests.get(self.url, headers=headers)
                    res.close()  # 关闭请求  释放内存
                except Exception as e:
                    print((start_, end_, "出错了,连接重试:%s", e,))
                    time.sleep(1)
                    continue
                flag = True

            # print("\n", ("%s-%s download success" % (start_, end_)), end="", flush=True)
            # with lock:
            with open(self.name, "rb+") as fd:
                fd.seek(start_)
                fd.write(res.content)
            # self.fd.seek(start_)                                        # 指定写文件的位置,下载的内容放到正确的位置处
            # self.fd.write(res.content)                                  # 将下载文件保存到 fd所打开的文件里

    def run(self, url, name):
        self.url = url
        self.name = name
        self.total = int(requests.head(url).headers['Content-Length'])
        # file_size = int(urlopen(self.url).info().get('Content-Length', -1))
        file_size = self.total
        if os.path.exists(name):
            first_byte = os.path.getsize(name)
        else:
            first_byte = 0
        if first_byte >= file_size:
            return file_size

        self.fd = open(name, "wb")  # 续传时直接rb+ 文件不存在时会报错,先wb再rb+
        self.fd.truncate(self.total)  # 建一个和下载文件一样大的文件,不是必须的,stream=True时会用到
        self.fd.close()
        # self.fd = open(self.name, "rb+")           # 续传时ab方式打开时会强制指针指向文件末尾,seek并不管用,应用rb+模式
        thread_list = []
        ts_queue = Queue()  # 用队列的线程安全特性，以列表的形式把开始和结束加到队列
        for ran in self.get_range():
            start_, end_ = ran
            ts_queue.put((start_, end_))

        for i in range(self.num):
            t = threading.Thread(target=self.download, name='th-' + str(i), kwargs={'ts_queue': ts_queue})
            t.setDaemon(True)
            thread_list.append(t)
        for t in thread_list:
            t.start()
        for t in thread_list:
            t.join()  # 设置等待，全部线程完事后再继续

        self.fd.close()

def sync():
    cwPath = "/www/py/cw"  # '/Users/luoshunkui/jpworkspace/cw/gpcw' #d:\\gjdata\\cw\\gpcw
    if sys.platform == 'win32' or sys.platform == 'cygwin':
        cwPath = "d:\\gjdata\\cw"
    if sys.platform=='darwin':
        cwPath='/Users/luoshunkui/userdata/tdx/cw'
    tdxFinance = TDXFinance(cwPath, ".pkl", "tdxSubjects.csv")
    tdxFinance.update()

def test():
    cwPath = "/www/py/cw"  # linux下财务数据存储地址
    if sys.platform == 'win32' or sys.platform == 'cygwin': # windows下的财务数据存储地址
        cwPath = "d:\\gjdata\\cw"
    if sys.platform=='darwin': # macos下的存储地址
        cwPath='/Users/userdata/tdx/cw'
    tdxFinance = TDXFinance(cwPath, ".pkl", "tdxSubjects.csv")
    # cats = tdxFinance.read_cat()
    # print(cats)
    # subjects = tdxFinance.read_subjects(0)
    # print(subjects)
    # x, y, z = 10, 20, 30
    # print(x)
    # print(y)
    # print(z)

    print(sys.argv)
    codes=[]
    date=''
    cats=tdxFinance.read_cat()
    print(cats)
    for arg in sys.argv:
        if arg.startswith('code='):
            codes=arg[5:].split(',')
        if arg.startswith('date='):
            date=arg[5:]
    for code in codes:
        infos = tdxFinance.get_all_infos(date, code)
        print(infos)
    if len(date)>0:
        infos=tdxFinance.get_all_finance(date)
        print(infos)
    # print(float(infos[506])/10000)
    # alls = tdxFinance.get_all_finance('20221231')
    # print(alls)
    # pf=alls.loc[alls[0].isin(['688778','603267'])]
    # print(pf)
    # alls1 = tdxFinance.get_all_finance('20210930')
    # alls2 = tdxFinance.get_all_finance('20200930')
    # alls3 = tdxFinance.get_all_finance('20190930')
    # pf = alls.loc[alls[0].isin(['002539', '000902', '002258'])]
    # print(pf)
    # npf = pf.T
    # print(npf)
    # print(npf.index)

    # nnpf = pd.merge(npf, subjects, left_index=True, right_on='code')
    # print(nnpf)

    # subject = 119
    # yi = 100000000
    # print(subjects.loc[subject])
    # sum2019 = alls3[subject].sum()
    # sum2020 = alls2[subject].sum()
    # sum2021 = alls1[subject].sum()
    # sum = alls[subject].sum()

    # print(sum2019 / yi)
    # print(sum2020 / yi)
    # print(sum2021 / yi)
    # print(sum / yi)

if __name__ == '__main__':

    if 'test' in sys.argv:
        test()
    else:
        sync()

