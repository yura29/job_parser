import argparse
import requests
from bs4 import BeautifulSoup
import json
import time
import sys
import os

# Константы
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'
}


######### Парсер #########


# Получаем страницу результатов поиска
def get_hh_resume_search_page(job_name, page_num):
    global HEADERS

    request_addr = 'https://hh.ru/search/resume?clusters=true&exp_period=all_time&logic=normal&no_magic=false&order_by=relevance&pos=full_text&text={0}&page={1}'.format(
        job_name, page_num)
    response = requests.get(request_addr, headers=HEADERS)

    return response


def get_res_pages_num(parsed_page):
    return int(parsed_page.findAll('a', {'data-qa': 'pager-page'})[-1].text)


def get_resume_url(resume_card):
    return 'https://hh.ru' + resume_card.find('a', {'class': 'resume-search-item__name'})['href']


# Строим из результтов парсера объект с данными о вакансии
def parse_resume(resume_url, search_phrase):
    res = {}
    try:
        response = requests.get(resume_url, headers=HEADERS)
        parsed_resume = BeautifulSoup(response.text)

        res['url'] = resume_url
        resume_name = parsed_resume.find('span', {'class': 'resume-block__title-text'})
        if resume_name != None:
            res['resume_name'] = resume_name.text
        res['profession'] = search_phrase

        specialization_name = parsed_resume.find('span', {'data-qa': 'resume-block-specialization-category'})
        if specialization_name != None:
            res['specialization'] = {}
            res['specialization']['name'] = specialization_name.text

            splecializations_list = parsed_resume.findAll('li', {'data-qa': 'resume-block-position-specialization'})
            if splecializations_list != None:
                res['specialization']['list'] = []
                for spec in splecializations_list:
                    res['specialization']['list'].append(spec.text)

        all_p = parsed_resume.findAll('p')
        for item in all_p:
            if item.text.startswith('График работы'):
                res['time'] = item.text.split(': ')[1]

        salary = parsed_resume.find('span', {'class', 'resume-block__salary'})
        if salary != None:
            res['salary'] = salary.text

        meta_info = parsed_resume.find('div', {'class': 'resume-header-block'})
        if meta_info != None:
            sex = meta_info.find('span', {'data-qa': 'resume-personal-gender'})
            if sex != None:
                res['sex'] = 0 if sex.text == 'Женщина' else 1

            age = meta_info.find('span', {'data-qa': 'resume-personal-age'})
            if age != None:
                res['age'] = int(age.text.split()[0])

            address = meta_info.find('span', {'data-qa': 'resume-personal-address'})
            if address != None:
                res['address'] = address.text.split()[0]

        about = parsed_resume.find('div', {'data-qa': 'resume-block-skills'})
        if about != None:
            res['about'] = about.text

        key_skills = parsed_resume.find('div', {'data-qa': 'skills-table'})
        if key_skills != None:
            res['key_skills'] = list(map(lambda x: x.text, key_skills.findAll('span', {'data-qa': 'bloko-tag__text'})))

        education = parsed_resume.find('div', {'data-qa': 'resume-block-education'}).find('div', {
            'class': 'resume-block-item-gap'}).find('div', {'class': 'resume-block-item-gap'})
        if education != None:
            res['education'] = []
            for education_item in education.findAll('div', {'class': 'bloko-columns-row'}):
                item_content = education_item.findAll('div')
                res['education'].append({'end_date': item_content[0].text, 'name': item_content[1].text})

        experience = parsed_resume.find('div', {'data-qa': 'resume-block-experience'})
        if experience != None:
            res['experience'] = {
                'total': experience.find('span', {'class': 'resume-block__title-text resume-block__title-text_sub'}).text}
            res['experience']['list'] = []
            for item in experience.find('div', {'class': 'resume-block-item-gap'}).findAll('div', {'itemprop': 'worksFor'}):
                tmp = {}
                tmp['company_name'] = item.find('div', {'itemprop': 'name'}).text
                tmp['time'] = item.find('div', {'class': 'resume-block__experience-timeinterval'}).text.replace(u'\xa0',
                                                                                                                u' ')
                tmp['position'] = item.find('div', {'data-qa': 'resume-block-experience-position'}).text
                tmp['duties'] = item.find('div', {'data-qa': 'resume-block-experience-description'}).text
                res['experience']['list'].append(tmp)

        languages = parsed_resume.find('div', {'data-qa': 'resume-block-languages'})
        if languages != None:
            res['languages'] = []
            for language in languages.findAll('p', {'data-qa': 'resume-block-language-item'}):
                data = language.text.split(' — ')
                res['languages'].append({data[0]: data[1]})
    except:
        res['msg'] = 'Fail. Caught exception'

    return res

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

parser = argparse.ArgumentParser()
parser.add_argument('-i', help='Input file names', nargs='+', required=True)
parser.add_argument('-o', help='Output dir', required=True)
parser.add_argument('-j', help='Job name', required=True)
args = parser.parse_args()

for input_path in args.i:
    total_urls = 0
    with open(input_path, 'r') as input:
        total_urls = sum(1 for line in input)

    with open(input_path, 'r') as input:
        progress_bar_len = 100
        printProgressBar(0, total_urls, prefix='Progress:', suffix='Complete', length=progress_bar_len)

        i = 0
        dir_path = '{0}/{1}'.format(args.o, args.j)
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)

        for link in input:
            link = link[:-1]
            id = link.replace('https://hh.ru/resume/', '')
            res = parse_resume(link, args.j)
            with open('{0}/{1}.json'.format(dir_path, id), 'w', encoding='utf8') as f:
                json.dump(res, f, ensure_ascii=False, indent=4)
            printProgressBar(i + 1, total_urls, prefix='Progress:', suffix='Complete', length=progress_bar_len)
            i += 1

