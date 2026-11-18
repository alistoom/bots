import time
from io import BytesIO
import operator

import requests
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


def submit_score():
    game_url = input("Game URL: ").strip()
    score = int(input("Score: ").strip())

    if "#" not in game_url:
        raise ValueError("The game URL must contain a # followed by its game ID.")

    unique_id = (game_url.split("#", 1)[1]).split("tgShareScoreUrl")[0][:-1]
    response = requests.post(
        "http://tbot.xyz/api/setScore",
        data={"data": unique_id, "score": score},
        timeout=20
    )
    response.raise_for_status()
    result = response.json()

    if "scores" in result:
        print("Score request completed.")
    else:
        print("The server did not accept the score.")


def lumberjack_instructions(screenshot, x):
    instructions = ["R" if x == 173 else "L"]

    for y in (414, 314, 214, 114, 14):
        instructions.append("R" if screenshot.getpixel((173, y))[0] == 161 else "L")

    return instructions


def lumberjack_click(body, instructions):
    for instruction in instructions:
        key = Keys.ARROW_LEFT if instruction == "L" else Keys.ARROW_RIGHT
        body.send_keys(key)
        time.sleep(0.05)
        body.send_keys(key)
        time.sleep(0.05)


def play_lumberjack():
    game_url = input("LumberJack game URL: ").strip()
    score_loop = int(input("Number of rounds (default 42): ").strip() or "42")

    driver = webdriver.Firefox()
    try:
        driver.set_window_size(300, 1000)
        driver.get(game_url)

        button_left = driver.find_element(By.ID, "button_left")
        body = driver.find_element(By.TAG_NAME, "body")
        button_left.click()
        body.send_keys(Keys.ARROW_LEFT)
        time.sleep(0.05)
        body.send_keys(Keys.ARROW_LEFT)
        time.sleep(0.05)

        canvas = driver.find_element(By.TAG_NAME, "canvas")
        for _ in range(score_loop):
            time.sleep(0.11)
            screenshot = Image.open(BytesIO(canvas.screenshot_as_png))
            x = 281 if screenshot.getpixel((281, 514))[0] == 161 else 173
            lumberjack_click(body, lumberjack_instructions(screenshot, x))
    finally:
        driver.quit()


def calculate_answer(x, operation, y):
    operations = {
        "+": operator.add,
        "-": operator.sub,
        "–": operator.sub,
        "*": operator.mul,
        "×": operator.mul,
        "/": operator.truediv,
        "÷": operator.truediv,
    }
    symbol = operation.strip()
    if symbol not in operations:
        raise ValueError(f"Unsupported operation: {symbol}")
    return int(operations[symbol](int(x), int(y)))


def play_math_battle():
    game_url = input("Math Battle game URL: ").strip()
    rounds = int(input("Number of questions (default 500): ").strip() or "500")

    driver = webdriver.Firefox()
    try:
        driver.get(game_url)
        button_correct = driver.find_element(By.ID, "button_correct")
        button_wrong = driver.find_element(By.ID, "button_wrong")
        text_x = driver.find_element(By.ID, "task_x")
        text_y = driver.find_element(By.ID, "task_y")
        text_operation = driver.find_element(By.ID, "task_op")
        text_result = driver.find_element(By.ID, "task_res")

        button_correct.click()
        for _ in range(rounds):
            x = text_x.get_attribute("innerHTML")
            y = text_y.get_attribute("innerHTML")
            operation = text_operation.get_attribute("innerHTML")
            given_result = text_result.get_attribute("innerHTML")
            answer = calculate_answer(x, operation, y)

            if str(answer) == given_result:
                button_correct.click()
            else:
                button_wrong.click()
    finally:
        driver.quit()


def main():
    print("1. Submit score")
    print("2. LumberJack browser automation")
    print("3. Math Battle browser automation")
    choice = input("Select mode: ").strip()

    if choice == "1":
        submit_score()
    elif choice == "2":
        play_lumberjack()
    elif choice == "3":
        play_math_battle()
    else:
        print("Invalid selection.")


if __name__ == "__main__":
    main()
