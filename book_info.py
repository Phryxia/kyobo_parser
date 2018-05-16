from bs4 import BeautifulSoup
import csv

# 책에 관한 간략한 정보를 담고 있는 클래스
class BookInfo:
    def __init__(self, title, author, translator, publisher, release, link):
        self.title = title
        self.author = author
        self.translator = translator
        self.publisher = publisher
        self.release = release
        self.link = link


# 책 정보를 필터링하는 조건모음입니다.
# 리스트에 들어있는 내용들은 OR로 처리됩니다.
class BookFilter:
    def __init__(self, name):
        self.name = name
        self.title = []
        self.author = []
        self.translator = []
        self.publisher = []

    def check(self, book_info):
        flag = True

        # 제목
        title_flag = False
        for _title in self.title:
            title_flag |= book_info.title.find(_title) != -1
        if len(self.title) > 0:
            flag &= title_flag

        # 지은이
        author_flag = False
        for _author in self.author:
            author_flag |= book_info.author.find(_author) != -1
        if len(self.author) > 0:
            flag &= author_flag

        # 옮긴이
        translator_flag = False
        for _translator in self.translator:
            translator_flag |= book_info.translator.find(_translator) != -1
        if len(self.translator) > 0:
            flag &= translator_flag

        # 출판사
        publisher_flag = False
        for _publisher in self.publisher:
            publisher_flag |= book_info.publisher.find(_publisher) != -1
        if len(self.publisher) > 0:
            flag &= publisher_flag

        return flag

    def __repr__(self):
        out = 'BookFilter[' + self.name + ']('
        out += 'title=' + self.title.__repr__()
        out += ', author=' + self.author.__repr__()
        out += ', translator=' + self.translator.__repr__()
        out += ', publisher=' + self.publisher.__repr__()
        out += ')'
        return out


# path로부터 XML 설정 파일을 열어, 구독하는 필터들을 불러옵니다.
# 설정파일은 다음과 같은 형식으로 이루어져야 합니다.
# 같은 종류의 태그끼리는 OR연산이며, 다른 종류의 태그끼리는 AND연산입니다.
#
# <root>
#   <filter name="라노벨">
#       <title>역시 내 청춘</title>
#       <title>단칸방의 침략자</title>
#   </filter>
#   <filter name="참고서">
#       <title>수학</title>
#       <author>홍성대</author>
#   </filter>
# </root>
#
# 사용 가능한 태그 종류: title, author, translator, publisher
def open_filter_config(path):
    filters = []

    f = open(path, 'r', encoding='utf-8')
    soup = BeautifulSoup(f.read(), 'xml')
    filter_tags = soup.find_all('filter')
    for filter_tag in filter_tags:
        book_filter = BookFilter(filter_tag['name'])
        filters.append(book_filter)
        
        # 제목
        title_tags = filter_tag.find_all('title')
        for title_tag in title_tags:
            book_filter.title.append(title_tag.string)
            
        # 지은이
        author_tags = filter_tag.find_all('author')
        for author_tag in author_tags:
            book_filter.author.append(author_tag.string)

        # 옮긴이
        translator_tags = filter_tag.find_all('translator')
        for translator_tag in translator_tags:
            book_filter.translator.append(translator_tag.string)

        # 출판사
        publisher_tags  = filter_tag.find_all('publisher')
        for publisher_tag in publisher_tags:
            book_filter.publisher.append(publisher_tag.string)

    f.close()
    return filters


# BookInfo 리스트에서 BookFilter를 만족하는 것들을
# 책장으로 만들어서 리스트로 뱉습니다.
def filter_books(book_list, book_filter):
    bookshelf = []
    for bookinfo in book_list:
        if book_filter.check(bookinfo):
            bookshelf.append(bookinfo)
    return bookshelf


# 책장을 csv파일로 저장합니다.
def save_bookshelf(name, bookshelf):
    f = open(name + '.csv', 'w', encoding='utf-8', newline='')
    wr = csv.writer(f)
    wr.writerow(['제목', '지은이', '옮긴이', '출판사', '발매일', '링크'])
    for book in bookshelf:
        temp = []
        temp.append(book.title)
        temp.append(book.author)
        temp.append(book.translator)
        temp.append(book.publisher)
        temp.append(book.release)
        temp.append(book.link)
        wr.writerow(temp)
    f.close()