교보파서(임시)는 교보문고의 신간을 체크하여, 원하는 서적 발매 여부를 csv 파일로 구독할 수 있는 프로그램입니다.
아직 일반 사용자가 사용할 수 있을 정도의 수준은 아니지만, 꾸준히 기능을 개선해 나갈 예정입니다.

~ 요구사항
python 3.6
BeautifulSoup(pip install bs4)
selenium(pip install selenium)
chromedriver(http://chromedriver.chromium.org/downloads)

* chromedriver가 있는 디렉토리를 PATH 변수에 등록해야합니다.

~ 사용법
1. config.xml을 열어서 구독하고자 하는 필터를 만듭니다.
1.1. <filter> 태그의 name 속성에 서재 이름을 적으시면 됩니다.
2. 터미널 혹은 cmd에 python main.py를 실행합니다.
3. 같은 폴더에 필터 이름별로 csv파일이 생성됩니다.
