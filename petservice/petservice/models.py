from django.db import models

class ImageFile(models.Model):
    id = models.AutoField(primary_key=True)
    path = models.CharField(max_length=3000)
    user_id = models.CharField(max_length=100, null=True)
    upload_date = models.DateTimeField(auto_now_add=True) # 업로드 날짜 자동 추가되도록 설정
    result0 = models.FloatField(max_length=100, null=True) # 백내장- 증상없음
    result1 = models.FloatField(max_length=100, null=True) # 백내장- 초기
    result2 = models.FloatField(max_length=100, null=True) # 백내장- 미성숙
    result3 = models.FloatField(max_length=100, null=True) # 백내장- 성숙

    def __str__(self):
        return str({"id": self.id,
                    "path": self.path,
                    "user_id" : self.user_id,
                    "upload_date": self.upload_date,
                    "result0" :self.result0,
                    "result1": self.result1,
                    "result2": self.result2,
                    "result3": self.result3})

class Article(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=500)
    main = models.CharField(max_length=7000)
    summary = models.CharField(max_length=2000, null=True)
    img_path = models.CharField(max_length=500, null=True)
    publisher = models.CharField(max_length=100, null=True)
    category = models.CharField(max_length=100, null=True)
    url = models.CharField(max_length=200, null=True)
    writedate = models.DateTimeField()

    def __str__(self):
        return str({'id': self.id,
                    'title': self.title,
                    'summary': self.summary,
                    'main' : self.main,
                    'img_path': self.img_path,
                    'publisher': self.publisher,
                    'category': self.category,
                    'url': self.url,
                    'writedate': self.writedate})

class Member(models.Model):
    id=models.CharField(primary_key=True, max_length=100)
    password = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    birthday = models.DateField()

    def __str__(self):
        return str({'id': self.id,
                    'password': self.password,
                    'name': self.name,
                    'email': self.email,
                    'birthday': self.birthday,
                    })

class Medical(models.Model):
    name = models.CharField(max_length=300)
    address = models.CharField(max_length=300)
    tel = models.CharField(max_length=300)
    lot = models.DecimalField(max_digits=10, decimal_places=4)
    lat = models.DecimalField(max_digits=10, decimal_places=4)

    class Meta:
        managed = False
        db_table = 'medical'
    
class MediclaConv(models.Model):
    name = models.CharField(max_length=1000)
    address = models.CharField(max_length=1000)
    tel = models.CharField(max_length=1000)
    lot = models.DecimalField(max_digits=10, decimal_places=7)
    lat = models.DecimalField(max_digits=10, decimal_places=8)

    class Meta:
        managed = False
        db_table = 'hospital'