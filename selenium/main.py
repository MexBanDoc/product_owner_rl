import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from PIL import Image, ImageEnhance
# import torch
# import numpy as np

#from pipeline.study_agent import load_dqn_agent
#from environment.environment import ProductOwnerEnv
#from game.game_variables import GlobalContext

import pytesseract
import cv2

screenshot_path = 'data/screenshot.png'

research_button_delta = (288, -150)
survey_button_delta = (288, -150)
hide_bottom_bar_button_delta = (220, 126)
show_bottom_bar_button_delta = (468, 126)
decompose_button_delta = (344, 210)

project_name_field_delta = (0, 80)
project_name_confirm_btn_delta = (0, 120)
tutorial_start_button_delta = (0, 140)
tutorial_top_button_delta = (96, -94)
tutorial_middle_button_delta = (-66, 125)
tutorial_bottom_button_delta = (-145, 131)

sprint_button_delta = (280, 206)
release_button_delta = (-365, 185)

users_count = 0
loyality = 0
sprint_number = 1
money = 120000
money_debt = 300000

backlog_start_x = 1090
backlog_start_y = 250
backlog_card_size = 50
backlog_max_count = 12
backlog_cards_delta = 6

sprint_start_x = 1216
sprint_start_y = 250
sprint_card_size = 50
sprint_max_count = 12
sprint_cards_delta = 6

userstory_start_x = 1090
userstory_start_y = 250
userstory_card_size_x = 110
userstory_card_size_y = 50
userstory_max_count = 6
userstory_cards_delta = 5

driver = webdriver.Chrome()

def main():
    # driver = webdriver.Chrome()
    driver.set_window_size(1280, 800)
    driver.get("https://npg-team.itch.io/product-owner-simulator")
    time.sleep(3)
    start_btn = driver.find_element(By.CLASS_NAME, "load_iframe_btn")
    start_btn.click()
    time.sleep(20)
    f = driver.find_element(By.ID, "game_drop")
    # while f == None:
    #     time.sleep(1)
    #     f = driver.find_element(By.ID, "game_drop")
    # actions = ActionChains(driver)
    ActionChains(driver).move_to_element(f).move_by_offset(*tutorial_start_button_delta).click().perform()
    ActionChains(driver).move_to_element(f).move_by_offset(*tutorial_start_button_delta).click().perform()
    ActionChains(driver).move_to_element(f).move_by_offset(*tutorial_start_button_delta).click().perform()
    ActionChains(driver).move_to_element(f).move_by_offset(*project_name_field_delta).click().send_keys("auto_manager").perform()
    ActionChains(driver).move_to_element(f).move_by_offset(*project_name_confirm_btn_delta).click().perform()
    ActionChains(driver).move_to_element(f).move_by_offset(*tutorial_top_button_delta).click().perform()
    ActionChains(driver).move_to_element(f).move_by_offset(*tutorial_top_button_delta).click().perform()
    ActionChains(driver).move_to_element(f).move_by_offset(*tutorial_top_button_delta).click().perform()
    ActionChains(driver).move_to_element(f).move_by_offset(*tutorial_middle_button_delta).click().perform()
    ActionChains(driver).move_to_element(f).move_by_offset(*tutorial_middle_button_delta).click().perform()
    ActionChains(driver).move_to_element(f).move_by_offset(*tutorial_bottom_button_delta).click().perform()
    ActionChains(driver).move_to_element(f).move_by_offset(*tutorial_bottom_button_delta).click().perform()
    ActionChains(driver).move_to_element(f).move_by_offset(*tutorial_bottom_button_delta).click().perform()

    ActionChains(driver).move_to_element(f).move_by_offset(*research_button_delta).click().perform()
    ActionChains(driver).move_to_element(f).move_by_offset(*tutorial_bottom_button_delta).click().perform()
    ActionChains(driver).move_to_element(f).move_by_offset(*hide_bottom_bar_button_delta).click().perform()
    time.sleep(3)
    ActionChains(driver).move_to_element(f).move_by_offset(*show_bottom_bar_button_delta).click().perform()
    time.sleep(3)

    ActionChains(driver).move_to_element(f).move_by_offset(280,-73).click().perform()
    ActionChains(driver).move_to_element(f).move_by_offset(280,-73).click().perform()
    ActionChains(driver).move_to_element(f).move_by_offset(*sprint_button_delta).click().perform()

    ActionChains(driver).move_to_element(f).move_by_offset(*tutorial_bottom_button_delta).click().perform()
    ActionChains(driver).move_to_element(f).move_by_offset(*tutorial_bottom_button_delta).click().perform()

    # ActionChains(driver).move_to_element(f).move_by_offset(273,-73).click().perform()
    ActionChains(driver).move_to_element(f).move_by_offset(*sprint_button_delta).click().perform()
    ActionChains(driver).move_to_element(f).move_by_offset(*tutorial_start_button_delta).click().perform()
    ActionChains(driver).move_to_element(f).move_by_offset(*tutorial_start_button_delta).click().perform()

    ActionChains(driver).move_to_element(f).move_by_offset(*tutorial_start_button_delta).click().perform()
    ActionChains(driver).move_to_element(f).move_by_offset(*tutorial_start_button_delta).click().perform()
    ActionChains(driver).move_to_element(f).move_by_offset(*tutorial_start_button_delta).click().perform()
    ActionChains(driver).move_to_element(f).move_by_offset(*tutorial_start_button_delta).click().perform()

    ActionChains(driver).move_to_element(f).move_by_offset(-144, -58).click().perform()
    ActionChains(driver).move_to_element(f).move_by_offset(-144, -58).click().perform()
    ActionChains(driver).move_to_element(f).move_by_offset(*tutorial_start_button_delta).click().perform()
    ActionChains(driver).move_to_element(f).move_by_offset(*tutorial_start_button_delta).click().perform()
    ActionChains(driver).move_to_element(f).move_by_offset(*tutorial_start_button_delta).click().perform()



    while True:
        g = 123

        driver.save_screenshot("data/screenshot.png")

        parse_backlog_cards()
        parse_userstory_cards()
        parse_state_data()
        parse_sprint_cards()

        # users_count = parse_number_from_screenshot("data/users.png")
        # loyality = parse_number_from_screenshot("data/loyality.png")
        # sprint_number = parse_number_from_screenshot("data/sprint_number.png")
        # money = parse_number_from_screenshot("data/money.png")
        # money_debt = parse_number_from_screenshot("data/money_debt.png")

def release(f):
    ActionChains(driver).move_to_element(f).move_by_offset(*release_button_delta).click().perform()

def sprint(f):
    ActionChains(driver).move_to_element(f).move_by_offset(*sprint_button_delta).click().perform()

def parse_state_data():
    Image.open(screenshot_path).crop((440, 52, 530, 72)).save("data/users.png")  # пользователи
    Image.open(screenshot_path).crop((420, 80, 480, 95)).save("data/loyality.png")  # лояльность
    Image.open(screenshot_path).crop((845, 50, 930, 73)).save("data/sprint_number.png")  # спринт
    Image.open(screenshot_path).crop((730, 75, 900, 95)).save("data/money.png")  # деньга

    Image.open(screenshot_path).crop((1240, 55, 1310, 75)).save("data/money_debt.png")  # долг
    Image.open(screenshot_path).crop((1250, 620, 1278, 632)).save(
        "data/used_sprint_hours.png")  # занятые часы спринта карта


def parse_userstory_cards():
    # Image.open(screenshot_path).crop((1090, 250, 1200, 300)).save("data/userstory_1.png")  # первая карта в юзерстори
    # # Image.open('data/screenshot.png').crop((1090, 305, 1200, 355)).save("data/userstory_type_2.png")  # вторая карта в юзерстори
    # Image.open(screenshot_path).crop((1105, 265, 1120, 283)).save(
    #     "data/userstory_type_1.png")  # первая карта в юзерстори
    # Image.open(screenshot_path).crop((1150, 262, 1200, 273)).save(
    #     "data/userstory_loyality_1.png")  # первая карта в юзерстори
    # Image.open(screenshot_path).crop((1150, 275, 1200, 290)).save(
    #     "data/userstory_users_1.png")  # первая карта в юзерстори
    cur_x = userstory_start_x
    cur_y = userstory_start_y
    for i in range(userstory_max_count):
        Image.open(screenshot_path)\
            .crop((cur_x, cur_y, cur_x+userstory_card_size_x, cur_y+userstory_card_size_y))\
            .save(f"data/userstory_{i}.png")
        cur_y += userstory_card_size_y + userstory_cards_delta

    cur_x = userstory_start_x
    cur_y = userstory_start_y
    for i in range(userstory_max_count):
        path = f"data/userstory_{i}.png"
        Image.open(path)\
            .crop((cur_x+15, cur_y+15, cur_x+15+15, cur_y+15+18))\
            .save(f"data/userstory_type_{i}.png")
        Image.open(path)\
            .crop((cur_x+60, cur_y+12, cur_x+userstory_card_size_x, cur_y+12+11))\
            .save(f"data/userstory_loyality_{i}.png")
        Image.open(path)\
            .crop((cur_x+60, cur_y+25, cur_x+userstory_card_size_x, cur_y+25+15))\
            .save(f"data/userstory_users_{i}.png")
        cur_y += userstory_card_size_y + userstory_cards_delta


def parse_backlog_cards():
    cur_x = backlog_start_x
    cur_y = backlog_start_y
    for i in range(backlog_max_count):
        Image.open(screenshot_path)\
            .crop((cur_x, cur_y, cur_x+backlog_card_size, cur_y+backlog_card_size))\
            .save(f"data/backlog_{i}.png")
        if i % 2 == 0:
            cur_x += backlog_card_size + backlog_cards_delta
        else:
            cur_y += backlog_card_size + backlog_cards_delta
            cur_x = backlog_start_x

def parse_sprint_cards():
    cur_x = sprint_start_x
    cur_y = sprint_start_y
    for i in range(sprint_max_count):
        Image.open(screenshot_path)\
            .crop((cur_x, cur_y, cur_x+sprint_card_size, cur_y+sprint_card_size))\
            .save(f"data/sprint_{i}.png")
        if i % 2 == 0:
            cur_x += sprint_card_size + sprint_cards_delta
        else:
            cur_y += sprint_card_size + sprint_cards_delta
            cur_x = sprint_start_x


def parse_number_from_screenshot(image_path: str):
    image = Image.open(image_path)
    enhancer = ImageEnhance.Sharpness(image)
    factor = 0.01  # чем меньше, тем больше резкость
    image = enhancer.enhance(factor)

    # string = pytesseract.image_to_data(image, config='--psm 6 -c tessedit_char_whitelist=+-0123456789,. ',
    #                                    output_type=pytesseract.Output.DICT)
    # print(string)

    image.save(image_path.split(".")[0]+"_sharp.png")
    result = pytesseract.image_to_string(image, config='--psm 6 -c tessedit_char_whitelist=+-0123456789,. ')
    print(result)
    return result


def parse_letter_from_screenshot(image_path: str):
    image = Image.open(image_path)
    enhancer = ImageEnhance.Sharpness(image)
    # factor = 0.01  # чем меньше, тем больше резкость
    # image = enhancer.enhance(factor)
    result = pytesseract.image_to_string(image, config='--psm 6 -c tessedit_char_whitelist=SMLX')
    print(result)
    return result


if __name__ == '__main__':
    #agent = load_dqn_agent("selenium/models/tutorial_agent.pt")

    # global_context = GlobalContext()
    #
    # env = ProductOwnerEnv()
    # agent.get_action()
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    main()