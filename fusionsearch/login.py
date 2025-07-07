import tempfile
from time import sleep

from fusionsearch import utils, config

from fusionsearch import log
import sys
import traceback
from urllib import request
import time

import cv2
import numpy as np

from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

TEMP_FOLDER = tempfile.gettempdir()
target_jpg_path = f'{TEMP_FOLDER}\\target.jpg'
template_png_path = f'{TEMP_FOLDER}\\template.png'

i_sys_user = config.i_sys_user
i_sys_password = config.i_sys_password

login_name_xpath = config.login_name_xpath
password_xpath = config.password_xpath
target_link_xpath = config.target_link_xpath
template_link_xpath = config.template_link_xpath
slider_xpath = config.slider_xpath


class CrackSlider():
    # 通过浏览器截图，识别验证码中缺口位置，获取需要滑动距离，并破解滑动验证码

    def __init__(self, url, driver=None):
        '''
        driver: 留空时自动获取
        url: 留空表示处理当前打开的页面
        '''

        super(CrackSlider, self).__init__()

        if driver is not None:
            self.driver = driver
        else:
            self.driver = utils.get_chrome()

        self.url = url
        self.wait = WebDriverWait(self.driver, 10)

    def get_pic(self, img_jpg_path, img_png_path):
        if self.url is not None:
            self.driver.get(self.url)

        self.driver.implicitly_wait(30)
        self.driver.find_element(By.XPATH, login_name_xpath).send_keys(i_sys_user)
        self.driver.find_element(By.XPATH, password_xpath).send_keys(i_sys_password, Keys.ENTER)
        time.sleep(3)

        target_link = self.driver.find_element(By.XPATH, target_link_xpath).get_attribute('src')
        template_link = self.driver.find_element(By.XPATH, template_link_xpath).get_attribute('src')

        req = request.Request(target_link)
        with open(img_jpg_path, 'wb+') as bg:
            bg.write(request.urlopen(req).read())

        req = request.Request(template_link)
        with open(img_png_path, 'wb+') as bk:
            bk.write(request.urlopen(req).read())

    def crack_slider(self, distance):
        slider = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, slider_xpath)))
        ActionChains(self.driver).click_and_hold(slider).perform()
        ActionChains(self.driver).move_by_offset(xoffset=distance, yoffset=0).perform()
        time.sleep(2)
        ActionChains(self.driver).release().perform()
        return 0


class SliderVerificationError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message
        self.stack_trace = traceback.format_exception(*sys.exc_info())

    def __str__(self):
        return self.message

    def stack_trace(self):
        return ''.join(self.stack_trace())


def add_alpha_channel(img):
    """ 为jpg图像添加alpha通道 """
    r_channel, g_channel, b_channel = cv2.split(img)  # 剥离jpg图像通道
    alpha_channel = np.ones(b_channel.shape, dtype=b_channel.dtype) * 255  # 创建Alpha通道

    img_new = cv2.merge((r_channel, g_channel, b_channel, alpha_channel))  # 融合通道
    return img_new


def handel_img(img):
    imgGray = cv2.cvtColor(img, cv2.COLOR_RGBA2GRAY)  # 转灰度图
    imgBlur = cv2.GaussianBlur(imgGray, (5, 5), 1)  # 高斯模糊
    imgCanny = cv2.Canny(imgBlur, 60, 60)  # Canny算子边缘检测
    return imgCanny


def match(img_jpg_path, img_png_path):
    # 读取图像
    img_jpg = cv2.imread(img_jpg_path, cv2.IMREAD_UNCHANGED)
    img_png = cv2.imread(img_png_path, cv2.IMREAD_UNCHANGED)
    # 判断jpg图像是否已经为4通道
    if img_jpg.shape[2] == 3:
        img_jpg = add_alpha_channel(img_jpg)
    img = handel_img(img_jpg)
    small_img = handel_img(img_png)
    res_TM_CCOEFF_NORMED = cv2.matchTemplate(img, small_img, 3)
    value = cv2.minMaxLoc(res_TM_CCOEFF_NORMED)
    value = value[3][0]  # 获取到移动距离
    return value


def login(url, driver=None):
    cs = CrackSlider(url, driver)
    log.info('1. 打开chromedriver，试试下载图片')
    cs.get_pic(target_jpg_path, template_png_path)
    log.info('2. 对比图片，计算距离')
    distance = match(target_jpg_path, template_png_path)
    distance = distance
    log.info('3. 移动')
    cs.crack_slider(distance)


def login_to_url(url, driver=None):
    login(url, driver)


def login_to_current_page(driver=None):
    login(driver.current_url, driver)


def login_by_n_time(n, url=None, driver=None):
    if not driver:
        driver = utils.get_chrome()
    title = driver.title
    for i in range(n):
        login_to_url(url, driver)
        sleep(3)
        log.info(f'当前Tab的title是：{driver.title}')
        if title != driver.title:
            log.info('已经跳转到其他页面，认为是登入成功')
            return

    raise SliderVerificationError(f'尝试{n}次自动滑块验证失败')


if __name__ == '__main__':
    wb = utils.get_chrome()
    wb.implicitly_wait(30)

    wb.get('http://10.160.28.16/uniLogin')
    if wb.title != '融合检索':
        login_by_n_time(3, url='http://10.160.28.16/uniLogin', driver=wb)
