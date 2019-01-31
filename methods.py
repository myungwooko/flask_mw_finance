from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
from db import User, Currency, Currency_info, db, app
from datetime import datetime
from operator import itemgetter



def page(url):
    pages = []
    count = 1
    while True:
        one = url + str(count)
        if count != 1:
            if requests.get(one).text != requests.get(pages[len(pages)-1]).text:
                pages.append(one)
                count += 1
            else:
                break
        else:
            pages.append(one)
            count += 1
    return pages




def finding_currency_name_by_id(id):
    currency = Currency.query.filter_by(id=id).all()[0]
    name = currency.name
    return name




def finding_currency_id_by_name(name):
    currency_id = Currency.query.filter_by(name=name).all()[0]
    return currency_id.id




def finding_currency_info_by_currency_id(currency_id):
    all = Currency_info.query.filter_by(currency_id=currency_id).all()
    if len(all) == 0:
        return None
    else:
        last_idx = len(all) - 1
        return all[last_idx]




def finding_html_line_by_name(name, pages):
    for page in pages:
        html = requests.get(page).text
        soup = BeautifulSoup(html, 'html.parser')
        for html_line in soup.select('tr'):
            title = html_line.select('.tit')
            if len(title) != 0:
                title = title[0].text
                if name == title:
                    return html_line



def trimming(html_line):
    trimmed_list = []
    rough = html_line.text.split('\n')
    for ele in rough:
        if len(ele) != 0 and ele != '\t\t\t\t\t\t\t' and ele != '\t\t\t\t\t\t':
            trimmed_list.append(ele)
    return trimmed_list




def insert_currency_info(trimmed_list):
    list = trimmed_list
    currency_id = finding_currency_id_by_name(list[0])

    #com_bef <= comparing_before <= 전일대비
    com_bef = list[3].split(' ')
    last_idx1 = len(com_bef) - 1
    com_bef = com_bef[last_idx1]

    currency_info = finding_currency_info_by_currency_id(currency_id)

    if currency_info == None or today_or_not(finding_currency_info_by_currency_id(currency_id)) is False:
        if len(trimmed_list[3:]) == 2:
            info = Currency_info(list[0], list[1], list[2], com_bef, '0.00%', currency_id)
            db.session.add(info)
            db.session.commit()
        else:
            plus_minus = list[4][len(list[4])-1]
            if plus_minus == '+':
                plus_minus_str = '▲'
            else:
                plus_minus_str = '▼'
            print()
            info = Currency_info(list[0], list[1], list[2], plus_minus_str + ' ' + com_bef, plus_minus + ' ' + '0' + list[len(list)-1].split('.')[1], currency_id)
            db.session.add(info)
            db.session.commit()






def find_today_currency_info_by_currency_id(currency_id):
    currency_infos = Currency_info.query.filter_by(currency_id=currency_id).all()
    if len(currency_infos) != 0:
        lastIdx = len(currency_infos) - 1
        return currency_infos[lastIdx]
    else:
        return None





def today_or_not(currency_info):
    if currency_info.created_on.strftime("%Y-%m-%d") ==  datetime.now().strftime("%Y-%m-%d"):
        return True
    else:
        return False





def dict_from_object(object):
    dict_info = {}
    dict_info['currency_id'] = object.currency_id
    dict_info['통화명'] = object.통화명
    dict_info['심볼'] = object.심볼
    dict_info['현재가'] = object.현재가
    dict_info['전일대비'] = object.전일대비
    dict_info['등락률'] = object.등락률
    dict_info['기준일'] = object.created_on.strftime("%Y.%m.%d")
    return dict_info





def find_and_insert(currency_id, pages):
    name = finding_currency_name_by_id(currency_id)
    html_line = finding_html_line_by_name(name, pages)
    trimmed_list = trimming(html_line)
    insert_currency_info(trimmed_list)




def case_currency_id_1_and_len_num(pages):
    today_ids = []
    not_today_ids = []
    result = []
    currency_infos = Currency_info.query.all()
    # 모든 통화에 대해 오늘것이 다들어와있다 한들 116개를 못넘으니까 거기에 록시나 몰라 여유롭게 1을 더해준 느낌
    currency_infos = currency_infos[:-118:-1]
    for one in currency_infos:
        if today_or_not(one):
            today_ids.append(one.currency_id)
    for id in range(2, 118):
        if id not in today_ids:
            not_today_ids.append(id)
    for id in not_today_ids:
        find_and_insert(id, pages)

    currency_infos = Currency_info.query.all()
    currency_infos = currency_infos[:-118:-1]
    for one in currency_infos:
        if today_or_not(one):
            one = dict_from_object(one)
            result.append(one)

    result = sorted(result, key=itemgetter('currency_id'))
    return jsonify(result)





def case_currency_id_1_and_len_zero(pages):
    result = []
    for page in pages:
        html = requests.get(page).text
        soup = BeautifulSoup(html, 'html.parser')
        count = 0
        for line in soup.select('tr'):
            if count == 0:
                count += 1
                pass
            else:
                trimmed_list = trimming(line)
                insert_currency_info(trimmed_list)
    all_info = Currency_info.query.all()

    for one in all_info:
        dict_info = dict_from_object(one)
        result.append(dict_info)
    return jsonify(result)






def case_currency_id_not_1(currency_id, pages):
    currency_info = find_today_currency_info_by_currency_id(currency_id)
    if currency_info is not None:
        there_is = today_or_not(currency_info)
        if there_is:
            return jsonify(dict_from_object(currency_info))
        else:
            find_and_insert(currency_id, pages)
            one = find_today_currency_info_by_currency_id(currency_id)
            return jsonify(dict_from_object(one))
    else:
        find_and_insert(currency_id, pages)
        info = find_today_currency_info_by_currency_id(currency_id)
        one = dict_from_object(info)
        return jsonify(one)
