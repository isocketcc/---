# encoding = utf-8
from tkinter import *
from tkinter.filedialog import *

import tkinter.messagebox
import psutil
import sys
import os
import requests
import ctypes
import re
import urllib
import time
import threading
import _thread
from bs4 import BeautifulSoup
import sys
import re
import codecs
import os
import shutil
import jieba
# 添加停用词
import jieba.analyse
import string
import math
req_header = {
"Referer":"http://novel.tingroom.com/tags.php?/%E5%8E%9F%E7%89%88%E8%8B%B1%E8%AF%AD%E5%B0%8F%E8%AF%B4/",
"Upgrade-Insecure-Requests":"1",
"User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36"
}
req_first_header = {
"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
"Accept-Encoding":"gzip, deflate",
"Accept-Language":"zh-CN,zh;q=0.8",
"Connection":"keep-alive",
"Cookie":"__gads=ID=4d15c6ee5c72d224:T=1508382776:S=ALNI_MaWmnddc0vOB0EWzmj37S_rE0C4Bg; bdshare_firstime=1508353977219; Hm_lvt_adaf29565debc85c07b8d3c36c148a6b=1508353979,1508354726,1508354857,1508392074; Hm_lpvt_adaf29565debc85c07b8d3c36c148a6b=1508394777; AJSTAT_ok_pages=18; AJSTAT_ok_times=2; yunsuo_session_verify=e228a28a013ddcdfebfbe1a7a3ea7fba",
"Host":"novel.tingroom.com",
"Upgrade-Insecure-Requests":"1",
"User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36"
}


pid_thread = 0
# 纪录控件状态
stateDelWord = 0
statePart = 0
stateCount = 0
stateMerge = 0
stateCalBack = 0
class Application():
    # 定义做界面的类
    root = Tk()
    BookNum = "2"
    fileName1 = " "
    fileName2 = " "
    # 添加滚动条
    scrollbar = Scrollbar(root)
    # 创建列表
    listbox = Listbox(root, )
    listbox.grid(row=1, column=0, columnspan=5, rowspan=90, sticky=S + N + W + E)

    def __init__(self, width=580, height=320):
        self.w = width
        self.h = height
        self.stat = True
        self.staIco = None
        self.stoIco = None

    def center(self):
        ws = self.root.winfo_screenwidth()
        hs = self.root.winfo_screenheight()
        x = int((ws / 2) - (self.w / 2))
        y = int((hs / 2) - (self.h / 2))
        self.root.geometry('{}x{}+{}+{}'.format(self.w, self.h, x, y))

    def GridBtn(self):
        # 创建按钮
        self.btnSpider = Button(self.root, command=self.eventSpiders, width=19, height=3)
        self.btnSpider.grid(row=0, column=0)
        self.btnDelWord = Button(self.root, text="分词并删除停用词",command = self.eventDelAndCutWord, width=19, height=3)
        self.btnDelWord.grid(row=0, column=1)
        self.btnContrast = Button(self.root, text="对比文档相似度", command = self.eventMarge, width=19, height=3)
        self.btnContrast.grid(row=0, column=2)
        self.btnQuit = Button(self.root, text="退出程序", command=self.root.quit, width=19, height=3)
        self.btnQuit.grid(row=0, column=3)

    def eventSpiders(self):
        if self.stat:  # 判断当前看控件的状态
            if self.get_section_stop():
                self.btnSpider["text"] = "启动爬虫"
                self.stat = False
        else:
            # 启动线程

            _thread.start_new_thread(self.get_english_text, (1,))
            self.stat = True
        self.btnSpider["state"] = "active"

    def eventDelAndCutWord(self):
        if self.stat:  # 判断当前看控件的状态
            if self.get_section_stop():
                self.stat = False
        else:
            # 启动线程
            try:
                _thread.start_new_thread(self.read_file_ED, (2,))
            except:
                self.listbox.insert(END, "线程启动失败!")
            self.stat = True
        self.btnDelWord["state"] = "active"

    def eventMarge(self):
        if self.stat:  # 判断当前看控件的状态
            if self.get_section_stop():
                self.stat = False
        else:
            stateSelect1 = self.SelectWin1()
            stateSelect2 = self.SelectWin2()
            # 启动线程
            if stateSelect1 and stateSelect2:
                try:
                    _thread.start_new_thread(self.merge_key, (5,))
                except:
                    self.listbox.insert(END, "线程启动失败!")
            self.stat = True
        self.btnContrast["state"] = "active"

    def loop(self):
        # 禁止改变窗口的大小
        self.root.resizable(False, False)  # 禁止修改窗口大小
        # 控件按钮
        self.GridBtn()
        self.center()
        self.eventSpiders()
        # 判断当前的控件状态 确保只有
        if stateDelWord == 1:
            self.eventDelAndCutWord()
        if stateMerge == 1:
            self.eventMarge()
        self.root.mainloop()

    # ===========================================================================================================
    # -----------------------------------------------网络爬虫----------------------------------------------------
    # 建立字典 存储信息
    def get_english_text(self,value):
        #清空listbox内容
        self.listbox.delete(0,END)
        # 定义文件路径
        res_path = "resEnglish\\res\\原文\\"
        req_url_base = "http://novel.tingroom.com"
        req_url_first = 'http://novel.tingroom.com/jingdian/'
        req_url_top = "http://novel.tingroom.com/jingdian/"
        i_top = 1
        # 记录下载的页面数
        i_page = 0
        # 定义元祖 存储页面地址
        url_first = ""
        while (i_top < 84):
            req_url = req_url_top + "list_1_" + str(i_top) + ".html"
            self.listbox.insert(END,"下载页面是:" + req_url)
            # 请求连接
            res = requests.get(req_url, params=req_header)
            # 格式转换
            source = BeautifulSoup(res.text, "html.parser")
            i_first = 0  # 二级页面地址
            while i_first < 10:
                # try:
                section_name = \
                source.select(".zhongvb .zhongz .zhongzxun1fvv .all003 .all001xp1 .list .text .yuyu a")[i_first]["href"]
                url_first = section_name
                req_url_first = req_url_base + url_first  # 二级页面地址
                self.listbox.insert(END,req_url_first)
                first_page = requests.get(req_url_first, params=req_first_header)
                first_page_text = BeautifulSoup(first_page.text, "html.parser")
                url_second = ""
                i_second = 0  # 三级页面标记
                while (1):
                    try:
                        flag_first = first_page_text.select(".zhongjjvvaa .zhongjjvvaa #body #content .box1 .clearfix li")[i_second].text
                        if (flag_first == '......'):
                            break
                        page_name = first_page_text.select(".zhongjjvvaa .zhongjjvvaa #body #content .box1 .vgvgd span")[0].text
                        url_second = first_page_text.select(".zhongjjvvaa .zhongjjvvaa #body #content .box1 .clearfix li a")[i_second]["href"]
                        chapter = first_page_text.select(".zhongjjvvaa .zhongjjvvaa #body #content .box1 .clearfix li a")[i_second]["title"]
                        req_url_second = req_url_first + "/" + url_second
                        # 进入每个页面开始下载
                        second_page = requests.get(req_url_second, req_first_header)
                        second_page_text = BeautifulSoup(second_page.text, "html.parser")
                        # 获取内容

                        second_page_contend = second_page_text.select(".zhongvbxxv #box_show #showmain .text")[0].text
                        # 将信息存入文件
                        # 打开文件
                        res_fo = open(res_path + str(i_page) + ".txt", "w")
                        res_fo.write("\r" + page_name + "\n")
                        # print(second_page_contend)
                        res_fo.write(str(second_page_contend.encode("GBK", "ignore")))
                        res_fo.close()
                        i_page = i_page + 1  # 下载页面数量增加1
                        i_second = i_second + 1
                        # name = page_name + chapter
                        # print(name+"下载完成!")

                    except:
                        print("连接失败")
                i_first = i_first + 1
            i_top = i_top + 1
        return TRUE
    # --------------------------------------------------- 分词并删除停用词----------------------------------------
    def read_file_ED(self,value):
        self.listbox.delete(0, END)
        # 定义文件的路径
        # 原文件所在路径
        path = "resEnglish\\res\\原文\\"
        # 停用词所在文件路径
        stop_path = "resEnglish\\res\\停用词\\停用词\\"
        # 删除停用词后文件路径后文件存储路径
        respath = "resEnglish\\res\\停用词\\res\\"
        num = 1
        # 加载通用词
        stop_file_E = stop_path + '英文停用词.txt'
        self.listbox.insert(END,stop_file_E)
        stop_word_fo = open(stop_file_E, 'r')  # 返回文件的对象
        stop_word = stop_word_fo.read()  # 获取停用词
        result_str = ""
        while num < 500:
            try:
                source_file_E = path + str(num) + ".txt"
                source_fo = open(source_file_E, 'rb')

                # 读取内容
                source_str = source_fo.read()
                # source_str = source_str.rsplit('\n')
                result_file_ED = respath + str(num) + "_D.txt"

                # 打开目标文件 向目标文件中写入
                result_fo = open(result_file_ED, 'w')
                # 首先将英文单词进行分词
                line = jieba.cut(source_str)
                for w in line:
                    if w not in stop_word:
                        result_str += w
                result_fo.write(result_str + "\n")
                self.listbox.insert(END,result_file_ED+"处理完毕!")
                result_str = " "  # 即使清空
                # source_str = source_fo.readline()
                result_fo.close()
                num = num + 1  # 处理文档数量加1
            except:
                print("文本读取出错")
        self.listbox.insert(END,"所有文档分词并删除停用词!")
        return TRUE

    # --------------------------------------统计函数---------------------------------------------
    def count_word(self,file_name):
        # 定义文件的路径
        path = "resEnglish\\res\\停用词\\res\\"
        res_path = "resEnglish\\res\\统计\\"
        # 文件的名称
        # file_num =3
        temp = str(file_name).split('/')
        source_file_name = file_name
        res_file_name = res_path + temp[len(temp) - 1] + "_EC.txt"
        # 统计关键词的个数
        # 计算机文件的行数
        line_nums = len(open(source_file_name, 'r', encoding='UTF-8').readline())
        # 统计格式是<key:value><属性:出现个数>
        i = 0
        # 定义字典 决定了统计的格式
        table = {}
        source_fo = open(source_file_name, "r", encoding='UTF-8')
        result_fo = open(res_file_name, "w")
        while i < line_nums:
            source_line = source_fo.readline()
            print("测试:"+source_line)
            # 将读取的字符用空格分割开
            words = str(source_line).split(" ")
            # 字典的插入与赋值
            for word in words:
                if word != " " and word != "\n" and word != "\t" and word in table:
                    num = table[word]
                    table[word] = num + 1
                elif word != "":  # 如果单词之前没有出现过
                    table[word] = 1
            i = i + 1
        # 将统计的键值排序
        dic = sorted(table.items(), key=lambda asd: asd[1], reverse=True)
        for i in range(len(dic)):
            result_fo.write("(" + dic[i][0] + ":" + str(dic[i][1]) + ")\n")
        source_fo.close()
        result_fo.close()
        return dic  # 函数返回值

    # ------------------------------------------计算余玄值----------------------------
    # 计算相似
    def merge_key(self,value):
        dic1 = []
        dic2 = []
        dic1 = self.count_word(self.fileName1)
        dic2 = self.count_word(self.fileName2)
        # 合并关键词
        array_key = []
        # 将文件1中的关键字添加到数组中去
        for i in range(len(dic1)):
            array_key.append(dic1[i][0])
        # 将文件2中的关键字添加到数组中去
        for i in range(len(dic2)):
            if dic2[i][0] not in array_key:  # 关键字在数组中已经出现过
                array_key.append(dic2[i][0])

        # 计算词频
        array_num1 = [0] * len(array_key)
        array_num2 = [0] * len(array_key)
        for i in range(len(dic1)):
            key = dic1[i][0]
            value = dic1[i][1]
            j = 0
            while j < len(array_key):
                if key == array_key[j]:
                    array_num1[j] = value
                    break
                else:
                    j = j + 1
        for i in range(len(dic2)):
            key = dic2[i][0]
            value = dic2[i][1]
            j = 0
            while j < len(array_key):
                if key == array_key[j]:
                    array_num2[j] = value
                    break
                else:
                    j = j + 1

        # 计算两个向量的点积
        x = 0
        i = 0
        while i < len(array_key):
            x = x + array_num1[i] * array_num2[i]
            i = i + 1

        # 计算两个向量的模
        i = 0
        sq1 = 0
        while i < len(array_key):
            sq1 = sq1 + array_num1[i] * array_num1[i]
            i = i + 1
        i = 0
        sq2 = 0

        while i < len(array_key):
            sq2 = sq2 + array_num2[i] * array_num2[i]
            i = i + 1
        try:
            result = float(x) / (math.sqrt(sq1) * math.sqrt(sq2))
        except:
            self.listbox.insert(END, "除数不能为零！")
        resultFloat = result
        #resultStr = "文档"+num1+"和"+ num2+"的相似度是:"+str(resultFloat)+"%"
        #创建新的窗口
        showRoot = Tk()
        label = Label(showRoot,text = "相似度:"+str(resultFloat),height = 7,width = 25)
        label.grid(row = 0)
        showRoot.mainloop()
        print(resultFloat)
        return True


    def SelectWin1(self):
        self.fileName1 = askopenfilename(filetypes=(("Text file", "*.txt*"), ("HTML files", "*.html;*.htm")))
        return True

    def SelectWin2(self):
        self.fileName2 = askopenfilename(filetypes=(("Text file", "*.txt*"), ("HTML files", "*.html;*.htm")))  # 显示打开文件对话框，并获取选择的文件名称
        return True

    # ---------------------------------------------------------停止----------------------------------------------
    def get_section_stop(self):

        return True


if __name__ == "__main__":
    w = Application()  # 创建对象并传递绑定的函数
    w.loop()
