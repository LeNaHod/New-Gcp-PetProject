from django.conf import settings
from datetime import datetime
from petservice.models import Article
from transformers import BartForConditionalGeneration, PreTrainedTokenizerFast
import torch

timeZone = datetime.now()

def schedule_api():
    print('### 기사 요약 시작')
    start = datetime.now()  # 시작 시간
    print('#### 기사 요약 시작 시간 : ', start.strftime('%Y-%m-%d %H:%M:%S'))

    # 토크나이저와 모델 불러오기
    model_path = 'C:\\workspaces\\webservice\\petservice\\static\\model\\kobart' #TODO 서버 컴에 맞춰 경로설정해주세용
    model = BartForConditionalGeneration.from_pretrained(model_path)
    tokenizer = PreTrainedTokenizerFast.from_pretrained('gogamza/kobart-base-v1')
    print('### 모델과 토크나이저 로드 완료')

    # Mysql DB에서 텍스트 불러오기
    articles = Article.objects.all()
    print('### article 테이블 데이터 개수 : ',len(articles))
    ids = []
    texts = []


    for article in articles:
        if article.summary:
            pass
        else:
            ids.append(article.id)
            texts.append(article.main)

    print(len(texts), len(ids))


    # 텍스트 전처리
    texts = [text.replace('\'', '\"') for text in texts]  # 작은 따옴표를 큰 따옴표로 변환한다.
    print('따옴표 변환 ', len(texts))
    texts = [text.replace('\n', ' ') for text in texts] # 줄 바꿈 문자를 띄어쓰기로 변환한다.
    print('줄바꿈 변환 ', len(texts))
    texts = [text.strip() for text in texts] # 맨 앞뒤의 공백을 제거한다.
    print('공백 제거 ', len(texts))


    for id, text in zip(ids, texts):
        print('### ', id,'> 글 요약 for 문 시작, 글자수 : ', len(text))
        if len(text)>2000:
            print(f'### {id} 번째 : 2000 넘어서 건너뜀')
            continue

        print(text[:20])
        text_encoding = tokenizer.encode(text)
        print('### 인코딩 완료')
        text_tensor = torch.tensor([text_encoding])
        print('### 텐서화 완료')
        result = model.generate(text_tensor, eos_token_id=1, max_length=256, num_beams=20, min_length=10)
        print('### 요약문 만들기')
        summary = tokenizer.decode(result[0], skip_special_tokens=True)
        print('### 디코딩 성공 : ', summary)

        article_update = Article.objects.filter(id=id)
        result_update = article_update.update(summary=summary)
        if result_update !=1:
            print(f'### {id} 번째 요약문 DB 저장 실패')

    end = datetime.now()  # 시작 시간
    print('#### 기사 요약 종료 시간 : ', end.strftime('%Y-%m-%d %H:%M:%S'))
    print('#### 기사 요약 소요 시간 : ', end - start)
    print('### 기사 요약 완료')

def check_running():
    print('### ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'), ' >>> background에서 스케줄러 가동 중입니다.')