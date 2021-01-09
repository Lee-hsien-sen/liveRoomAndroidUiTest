from page.studentPage import studentPage, log, Keys
import commons.page_elements as page_elements
import time
import random

# from lxml import etree


class Method(studentPage):
    '''方法类'''

    def __init(self, live_id):
        studentPage.__init__(self, live_id)

    def ansChoiceQ(self, rightAns="A", ansnum=4, isright=True, ishalfright=False):
        """作答选择题
        @rightAns     正确答案 str 可传多位表示多选 空表示为投票题
        @ansnum       答案选项
        @isright      是否全对
        @ishalfright  是否半对
        """
        ans = ["A", "B", "C", "D", "E", "F", "G", "H"]
        ans = ans[:ansnum]
        rightAns = rightAns.upper()
        if not self.is_elements_visibility(page_elements.vote.page_css, by="css"):
            log.info("未出现选择题面板")
            return
        ans_btn = page_elements.vote.ans_btn
        submit_btn = page_elements.vote.submit_btn
        close_btn = page_elements.vote.close_btn
        if not rightAns:
            anyAns = random.choice(ans)
            self.do_click(ans_btn.format(anyAns))
        elif len(rightAns) == 1:
            ans.remove(rightAns)
            wrongAns = random.choice(ans)
            if isright:
                self.do_click(ans_btn.format(rightAns))
            else:
                self.do_click(ans_btn.format(wrongAns))
        else:
            if isright:
                self.do_click(ans_btn.format(rightAns[0]))
                if not ishalfright:
                    for i in rightAns[1:]:
                        self.do_click(ans_btn.format(i))
            else:
                for i in rightAns:
                    ans.remove(i)
                wrongAns = random.choice(ans)
                self.do_click(ans_btn.format(wrongAns))
        self.do_click(submit_btn)
        if self.is_elements_visibility(close_btn):
            self.do_click(close_btn)
        else:
            return

    def ansVenusQ(self, rightAns="A", ansnum=4, isright=True, ishalfright=False):
        """作答Venus题
        @rightAns     正确答案 可传list/str list为多题 str可传多位表示多选
        @ansnum       答案选项
        @isright      是否全对
        @ishalfright  是否半对
        """
        if self.classType != 1:
            log.info("课型暂不支持")
            return
        ans = ["A", "B", "C", "D", "E", "F", "G", "H"]
        ans = ans[:ansnum]
        rightAns = rightAns.upper()
        if not self.is_elements_visibility(page_elements.venus.page, by="css"):
            log.info("未出现venus答题面板")
            return
        ans_btn = page_elements.venus.ans_btn
        submit_btn = page_elements.venus.submit_btn
        close_btn = page_elements.venus.close_btn

        def _doAns(rightAns, ans):
            if len(rightAns) == 1:
                ans.remove(rightAns)
                wrongAns = random.choice(ans)
                if isright:
                    self.do_click(ans_btn.format(rightAns))
                else:
                    self.do_click(ans_btn.format(wrongAns))
            else:
                if isright:
                    self.do_click(ans_btn.format(rightAns[0]))
                    if not ishalfright:
                        for i in rightAns[1:]:
                            self.do_click(ans_btn.format(i))
                else:
                    for i in rightAns:
                        ans.remove(i)
                    wrongAns = random.choice(ans)
                    self.do_click(ans_btn.format(wrongAns))
            self.do_click(submit_btn)
            time.sleep(3)

        if isinstance(rightAns, str):
            _doAns(rightAns, ans)
        else:
            for index in rightAns:
                _doAns(index, ans)
        self.driver.switch_to.default_content()
        if self.is_elements_visibility(close_btn):
            self.do_click(close_btn)
        else:
            return

    def ansAudioQ(self):
        """作答语音题"""
        if self.is_elements_visibility(page_elements.audio.page):
            self.do_click(page_elements.audio.ans_btn, by="css")
            time.sleep(3)
            self.do_click(page_elements.audio.ans_btn, by="css")
            time.sleep(1)
            self.do_click(page_elements.audio.close_btn)
        else:
            log.info("未出现语音题答题面板")
            return

    def closeMVPbutton(self):
        """关闭MVP弹窗"""
        if self.is_elements_visibility(page_elements.vote.mvp_page):
            self.do_click(page_elements.vote.mvp_close_btn)

    def sendChat(self, txt):
        """发送聊天
        @txt        信息str
        @classType  课程类型 1/2 三分屏/小班课
        """
        num = 0 if self.classType == 2 else 1
        self.move_by_coordinate(50, 50)
        self.do_click(page_elements.chat.nomal_chat_label, num=num)
        self.input_text(txt, page_elements.chat.nomal_chat_label, num=num)
        self.input_text(
            Keys.ENTER, page_elements.chat.nomal_chat_label, nedclear=False, num=num)

    @property
    def isfullScreen(self):
        if self.classType == 2:
            lable = self.find_element_test(page_elements.livetype.title)
            lable = lable.get_attribute("class")
            if lable == page_elements.livetype.smallclass_live_fullscreen:
                log.info("当前为全屏")
                return True
            else:
                log.info("当前为非全屏")
                return False

    def toggleScreen(self):
        """切换全屏/非全屏"""
        if self.classType == 2:
            if self.isfullScreen:
                self.move_by_coordinate(50, 50)
            self.do_click(page_elements.togglescreen.change_btn, by="css")
        log.info("切换成功")

    def openRankingList(self, ranklistType=1):
        """打开排行榜
        @ranklistType 打开海星/答题榜 1/2
        """
        if self.classType == 2:
            if self.isfullScreen:
                self.move_by_coordinate(50, 50)
            self.do_click(
                page_elements.rangkinglist.small_class_rank_btn, by="css")
            if ranklistType == 2:
                self.do_click(page_elements.rangkinglist.ans_rank_btn)

    @property
    def hasChangeFrame(self):
        if self.classType == 2:
            if self.is_elements_visibility(page_elements.listencarefully.page, by="css"):
                self.do_click(page_elements.listencarefully.btn, by='css')
                return True
        return False

    @property
    def isChatClose(self):
        """关闭聊天按钮状态"""
        if self.isfullScreen:
            self.move_by_coordinate(50, 50)
        if self.is_elements_exist(page_elements.chat.close_btn, by="css"):
            return False
        if self.is_elements_exist(page_elements.chat.open_btn, by="css"):
            return True
        log.info("未找到控件")

    def changeChatStatus(self):
        """改变聊天按钮状态"""
        if self.isChatClose:
            self.do_click(page_elements.chat.open_btn, by="css")
            log.info("关闭聊天成功")
        else:
            self.do_click(page_elements.chat.close_btn, by="css")
            log.info("打开聊天成功")

    def sendEmoticon(self, emoteType=1):
        """发送表情
        @emoteType 表情类型 1/2/3/6   1/2/ok/666
        """
        dic = {1: "1", 2: "2", 3: "OK", 6: "666"}
        if self.classType == 2:
            if self.isfullScreen:
                self.move_by_coordinate(50, 50)
            self.do_click(page_elements.emotion.smallclass_emote_btn, by="css")
            body_html = self.find_element_test(
                page_elements.livetype.smallclass_body_center)
            body_html.find_element_by_css_selector(
                page_elements.emotion.container).find_element_by_xpath(page_elements.emotion.btn.format(dic[emoteType])).click()

    def changeLines(self):
        """切换线路"""
        if self.classType == 2:
            if self.isfullScreen:
                self.move_by_coordinate(50, 50)
            body_html = self.find_element_test(
                page_elements.livetype.smallclass_body_center)
            body_html.find_element_by_css_selector(
                page_elements.changelines.menu_btn).click()
            res = body_html.find_element_by_css_selector(
                page_elements.changelines.menu_ele)
            choiceline = res.find_element_by_css_selector(
                page_elements.changelines.choice_line).text
            log.info("当前线路:" + choiceline)
            res1 = res.find_elements_by_xpath(
                page_elements.changelines.lines_xpath.format("线路"))
            Linelist = [i.text for i in res1 if i.text]
            log.info(Linelist)
            Linelist.remove(choiceline)
            changeline = random.choice(Linelist)
            log.info("切换线路:" + changeline)
            res.find_element_by_xpath(
                page_elements.changelines.lines_xpath.format(changeline)).click()


if __name__ == "__main__":
    # 5f64227c4d04ca1e49f4055b  三分屏
    # 5f6960ad4d04ca1e49f4073b  小班课
    stu = Method(live_id="5f714ee253ffbd39c9e6e10c")
    # num=input("请选择本次执行的学生数: ")
    num = 2
    num = int(num)
    stu.openstudentend(num)
    print("X" * 80)
    # stu.sendChat("123")
    # stu.sendEmoticon()
    # stu.ansVenusQ()
    # stu.toggleScreen()
    # time.sleep(1)
    # stu.isChatClose
    # stu.toggleScreen()
    # stu.changeLines()
