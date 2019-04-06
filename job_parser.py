# Вакансии, которые мы будем искать
# Формат: {'name': 'JobName', 'request': 'request': 'https://hh.ru/search/resume?blablabla'}
jobs = [
    {
        'name': 'Бортпроводник',
        'request': 'https://hh.ru/search/resume?text=%D0%B1%D0%BE%D1%80%D1%82%D0%BF%D1%80%D0%BE%D0%B2%D0%BE%D0%B4%D0%BD%D0%B8%D0%BA&area=1&clusters=true&exp_period=all_time&logic=normal&pos=full_text'
    }
]

# Необходимые библиотеки
import requests
from bs4 import BeautifulSoup
import json

# Константы
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'
}


######### Парсер #########


# Получаем страницу результатов поиска
def get_hh_resume_search_page(job_name, page_num):
    global HEADERS

    request_addr = 'https://hh.ru/search/resume?text={0}&page={1}'.format(job_name, page_num)
    response = requests.get(request_addr, headers=HEADERS)

    return response


def get_resume_url(resume_card):
    return 'https://hh.ru' + resume_card.find('a', {'class': 'resume-search-item__name'})['href']


def get_res_pages_num(parsed_page):
    return int(parsed_page.findAll('a', {'data-qa': 'pager-page'})[-1].text)

# Print iterations progress
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
    # Print New Line on Complete
    if iteration == total:
        print()


for job in jobs:
    print('Парсинг вакансии {0}'.format(job['name']))
    resume_urls_f = open('resume_lists/{0}_urls.txt'.format(job['name']), 'w+')
    # Получаем страницу с резюме по запросу
    resume_page = requests.get(job['request'], headers=HEADERS)
    print('Поиск по запросу {0}'.format(resume_page.url))
    # Парсим страницу
    parsed_page = BeautifulSoup(resume_page.text)
    pages_num = get_res_pages_num(parsed_page)
    print('Всего получено страниц поиска {0}'.format(pages_num))

    total_parsed = 0
    for page_num in range(pages_num):
        resume_page = get_hh_resume_search_page(job['name'], page_num)
        parsed_page = BeautifulSoup(resume_page.text)
        # Получаем все карточки резюме с этой страницы
        resumes_cards = parsed_page.findAll('div', {'class': 'resume-search-item__content-wrapper'})

        progress_bar_len = 100
        page_urls = ''
        for index, resume in enumerate(resumes_cards):
            page_urls += get_resume_url(resume).split('?')[0] + ' ' + job['name'] + '\n'

        resume_urls_f.write(page_urls)
        total_parsed += 1

        printProgressBar(total_parsed, pages_num, prefix='Progress:', suffix='Complete', length=progress_bar_len)

