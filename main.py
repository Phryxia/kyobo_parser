from selenium import webdriver
from bs4 import BeautifulSoup
from book_info import *
import re
import sys


'''
    TODO:
        국내도서/국외도서 선택
        텔레그램 봇이랑 연동시키기
'''


# website list
KYOBO_KOR_BOOK = 'http://www.kyobobook.co.kr/newproduct/newProductKorList.laf'
KYOBO_ENG_BOOK = 'http://www.kyobobook.co.kr/newproduct/newProductEngList.laf'
KYOBO_KOR_DETAIL = 'http://www.kyobobook.co.kr/product/detailViewKor.laf'
KYOBO_ENG_DETAIL = 'http://www.kyobobook.co.kr/product/detailViewEng.laf'


# 신간 정보가 담겨있는 태그인지 분석합니다.
def is_book_info(tag):
    return tag.name == 'dl' and tag.get('class')[0] == 'book_title'


# 단어를 제외한 공백을 모두 제거합니다. 입력으로 주로 이런게 들어옵니다.
# ex) '\n\t\t\t\t\t\t\t\t\t\t\t\t\tGayford, Martin' -> 'Gayford, Martin'
def refine_blanked_string(word):
    return word.strip('\n\t ')


# 출간날짜에 섞인 노이즈를 없앱니다.
# ' | YYYY년 MM월 DD일 '이 들어옵니다.
def refine_release_date(word):
    # return word[3:-1]
    return re.compile('[0-9]{4}년 [0-9]{2}월 [0-9]{2}일').findall(word)[0]


# 개별상품 페이지 이동 스크립트로부터, 명시적인 제품 상세 URL을 추출합니다.
#
# ex) javascript:goDetailProductNotAge('KOR','070521','9791196191917','0 ', 'N')
#   -> http://www.kyobobook.co.kr/product/detailViewKor.laf?mallGb=KOR&ejkGb=KOR&linkClass=070521&barcode=9791196191917
def extract_product_url(script):
    params = re.compile('\'[0-9A-Za-z^,]+\'').findall(script)
    locale = params[0][1:-1]
    link_class = params[1][1:-1]
    barcode = params[2][1:-1]
    if locale == 'KOR':
        url = KYOBO_KOR_DETAIL
    else:
        url = KYOBO_ENG_DETAIL
    return url + '?mallgb=' + locale + '&ejkGb=' + locale + '&linkClass=' + link_class + '&barcode=' + barcode


# 페이지 이동 스크립트를 selenium이 실행할 수 있도록 가공합니다.
# 'javascript: go_targetPage("n")'이 들어옵니다.
def refine_next_script(script):
    return script[11:]


# 책 정보가 담긴 <dl> 태그를 읽어서, 책 정보를 추출합니다.
# 출판사 추출이 좀 까다로운데, 책에 따라서 형식이 다르기 때문입니다.
#
# len(contents) == 7  -> [저자, <span>지음</span>, \n, |, 출판사, <span>| 날짜</span>, \n]
# len(contents) == 9  -> [저자, <span>지음</span>, \n, |, 출판사, <span>| 날짜</span>, \n, 인쇄버전, \n]
# len(contents) == 11 -> [저자, <span>지음</span>, \n, |, <span>번역가</span>, \n, |, 출판사, <span>| 날짜</span>, \n]
def parse_book_info(tag):
    link = tag.find('a')
    title = refine_blanked_string(link.string)
    infos = tag.find('dd').contents
    author = refine_blanked_string(infos[0])
    if len(infos) >= 11:
        translator = refine_blanked_string(infos[4].string)
        publisher = refine_blanked_string(infos[8])
        release = refine_release_date(infos[9].string)
    else:
        translator = ''
        publisher = refine_blanked_string(infos[4])
        release = refine_release_date(infos[5].string)
    return BookInfo(title, author, translator, publisher, release, extract_product_url(link.get('href')))


# 현재 보고 있는 페이지를 탐색합니다.
# 더 탐색할 페이지가 있으면 driver로 다음 페이지를 부른 뒤
# true를, 아니면 false를 반환합니다.
#
# <dl class="book_title>
#   <dt>
#       <strong><a href="script" target="_parent">TITLE</a></strong>
#       <span ...></span>
#   <dt>
#   <dd>
#       Author
#       <span class="Publisher">지음</span>
#       <span>|</span>
#       Publisher
#       <span class="Publisher"> | YYYY년 MM월 DD일</span>
#   </dd>
#   ...
# ...
def parse_page(driver, out):
    print('새 페이지 탐색 중...')
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    book_infos = soup.find_all(is_book_info)
    for book_info_tag in book_infos:
        out.append(parse_book_info(book_info_tag))

    # 다음 페이지가 있는지 봅니다.
    # 교보문고의 경우, 마지막 페이지임에도 버튼은 사라지지 않습니다.
    # 이동할 수 있는 경우, <a> 태그로 감싸져 있습니다.
    next_link = soup.find('img', alt='다음 페이지로 이동').parent
    if next_link.name == 'a':
        driver.execute_script(refine_next_script(next_link['href']))
        return True
    else:
        return False


def main():
    # argument parsing
    show_browser = False
    idx = 1
    while idx < len(sys.argv):
        if sys.argv[idx] == '--debug':
            show_browser = True
        idx += 1

    # webdriver setup
    option = webdriver.ChromeOptions()
    if not show_browser:
        option.add_argument('headless')
    driver = webdriver.Chrome(chrome_options=option)

    try:
        # load webpage
        driver.get(KYOBO_KOR_BOOK)
        driver.implicitly_wait(8)

        # crawl webpage
        print('신간 정보를 불러옵니다.')
        new_books = []
        while parse_page(driver, new_books):
            pass

        # outcome
        print('서재를 정리하여 파일로 저장합니다.')
        filters = open_filter_config('config.xml')
        for book_filter in filters:
            bookshelf = filter_books(new_books, book_filter)
            save_bookshelf(book_filter.name, bookshelf)
    except:
        print('어디선가 에러가 발생했는데 알게 뭐야')

    # close webdriver
    driver.close()


if __name__ == '__main__':
    main()