from django import forms
from django.contrib.auth.models import User
from .models import Account

# フォームクラス作成
class AccountForm(forms.ModelForm):
    # パスワード入力：非表示対応
    password = forms.CharField(widget=forms.PasswordInput(),label="パスワード")

    class Meta():
        # ユーザー認証
        model = User
        # フィールド指定
        fields = ('username','password')
        # フィールド名指定
        labels = {'username':"ユーザーID"}

class AddAccountForm(forms.ModelForm):
    class Meta():
        # モデルクラスを指定
        model = Account
        fields = ()

from .models import NiftyFile

class uploadForm(forms.ModelForm):
    class Meta():
        model=NiftyFile
        fields=['file']


class SelectForm(forms.Form):
    
    def __init__(self, user, *args, **kwargs):
        super(SelectForm, self).__init__(*args, **kwargs)
        self.fields['upfiles'] = forms.ModelChoiceField(
            NiftyFile.objects.filter(user=user),
            label='selected'
        )

