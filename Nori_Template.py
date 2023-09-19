#데이터 마켓 구축을 위한 News기사에 적용시킬 Template지정

PUT _template/noritemplate #7.11버전이상부터는 _index_template 
{
"index_patterns" : [ #적용받을 인덱스명의 패턴지정
      "nori_*"  #nori_~ 로 시작하는 파일을은 모두 해당 탬플릿구조를따른다.
    ],
    "order": 1,
    "settings": { 
		"number_of_shards": 1,
		"number_of_replicas": 1,
		"index":{
			"analysis":{ 
				"tokenizer":{ !
					"nori_mixed":{ #nori_mixed라는 이름으로 커스텀 토크나이저 설정.
						"type":"nori_tokenizer", # nori 토크나이저 지정
						"decompound_mode":"mixed" 
					}
				},
				"analyzer":{
					"nori_a":{ #분석기이름
						"type":"custom", 
						"tokenizer":"nori_mixed" #위에서 만든 Nori토크나이저 사용
					}
				}	
			}	
		}
    },
   "mappings": {  # mysql에서 id,title,main,date컬럼을 가져올것이여서 가져올 데이터들이 엘라스틱에 저장될 필드를 지정한다.
      "properties": {
        "id": {
          "type": "integer"
        },
        "title": {
          "type": "text",
          "fields": {
            "title_keyword": {
              "type": "keyword",
              "ignore_above": 256
            }
          }
        },
        "main": {
          "type": "text",
					"analyzer":"nori_a",
          "fields": {
            "main_keyword": {
              "type":"keyword"
            }
          }
        },
        "write_date": {
          "type": "date",
          "format": "yyyy.MM.dd HH:mm||iso8601||yyyy.MM.dd||yyyy-MM-dd HH:mm"
        }
      }
    }
  }

