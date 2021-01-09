class venus:
    page = "[class='examination-wrapper js-examination-wrapper']"
    ans_btn = "//div[contains(@class,'vp-option-item-code') and contains(@class,'vp-font-bold') and contains(text(),'{}')]"
    submit_btn = "//div[contains(text(),'提交') and contains(@class,'vp-submit-btn')]"
    close_btn = "//span[contains(@class,'close_btn')]"


class livetype:
    title = "//body[@id='box']"
    ordinary_live = "student"
    smallclass_live = "super-small-class"
    smallclass_live_fullscreen = "student super-small-class line_to_top line_to_bottom super-small-class-full-screen"
    smallclass_body_center = "//div[contains(@class,'player-wrapper')]"


class vote:
    page_css = "[class='classworkForg super-small-class-work-forg js-class-work-forg']"
    page_xpath = "//div[ contains(@class,'classworkForg') and contains(@class,'super-small-class-work-forg') and contains(@class,'js-class-work-forg')]"
    ans_btn = "//li[ contains(@class,'option') and contains(@as,'{}')]"
    submit_btn = "//div[contains(text(),'提交') and contains(@id,'workButton')]"
    close_btn = "//span[contains(@class,'close_btn')]"
    mvp_page = "//div[contains(@class,'answer-star-mask') and contains(@id,'js-answer-mask')]"
    mvp_close_btn = "//div[contains(@class,'answer-close') and contains(@id,'js-answer-close')]"


class audio:
    page = "//div[ contains(@class,'score-bg') and contains(@id,'js-score-bg')]"
    ans_btn = "[class='audio-pic audio-noactive js-audio-pic']"
    close_btn = "//span[contains(@class,'close_btn')]"


class prejoinpage:
    public_class_tag = "//li[ contains(text(),'公开课')]"
    web_student_joinclass_btn = "//button[ contains(text(),'学生进入房间') and contains(@data-for-device,'4')]"


class chat:
    nomal_chat_label = "//textarea[contains(@placeholder,'请输入聊天信息') and contains(@class,'chatContent')]"
    close_btn = "[class='close-chat-btn js-close-chat-btn']"
    open_btn = "[class='close-chat-btn js-close-chat-btn close-chat-btn-unchecked']"


class togglescreen:
    change_btn = "[class='full-screen-btn icon-btn-box js-full-screen-btn']"


class floatinglayer:
    hide_css = "[class='big-body-foot-line js-big-body-foot-line js-player-control-bar player-foot-bar-show green-live hide']"


class rangkinglist:
    small_class_rank_btn = "[class='rank-btn text-btn js-rank-btn']"
    stars_rank_btn = "//div[@id='js-starfish',@mode='starfishmode']"
    ans_rank_btn = "//div[@id='js-subject',@mode='submode']"


class changelines:
    menu_btn = "[class='js-change-route switch-route-line icon-btn-box']"
    menu_ele = "[class='route-container']"
    choice_line = "[class='route-link route-selected']"
    lines_xpath = "//span[contains(text(),'{}')]"


class emotion:
    smallclass_emote_btn = "[class='emoticon-btn icon-btn-box js-emoticon']"
    container = "[class='emotion-container']"
    btn = "//img[contains(@data-lable,'{}')]"

class listencarefully:
    page="[class='stars-mask student-listen-carefully js-student-listen-carefully']"
    btn="[class='student-listen-carefully-btn js-student-listen-carefully-btn']"