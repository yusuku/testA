from django.db import models
# ユーザー認証
from django.contrib.auth.models import User

# ユーザーアカウントのモデルクラス
class Account(models.Model):

    # ユーザー認証のインスタンス(1vs1関係)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ObjsUrls=models.TextField(blank=True)
    file = models.FileField()
    def __str__(self):
        return self.user.username
    


    
def savePath(instance, filename):
    
    return 'user_{0}/{1}'.format(instance.user.id, filename)


class NiftyFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(
        upload_to=savePath,
        verbose_name='添付ファイル',
    )
    def __str__(self):
        return self.file.name.split('/')[-1]

class ObjFile(models.Model):
    file = models.FileField()
    niftyfile = models.ForeignKey(NiftyFile, on_delete=models.CASCADE)

   