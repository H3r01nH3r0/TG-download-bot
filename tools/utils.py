from json import load, dump
from typing import List


def get_config(filename: str) -> dict:
    with open(filename, "r", encoding="utf-8") as file:
        data: dict = load(file)
    return data


def save_config(filename: str, data: dict) -> None:
    with open(filename, "w", encoding="utf-8") as file:
        dump(data, file, indent=4, ensure_ascii=False)


def generate_list(post_list: List, value: int = 5) -> List[List]:
    result = list()
    while len(post_list) > 5:
        row = post_list[:value]
        result.append(row)
        post_list = post_list[value:]
    result.append(post_list)
    return result
