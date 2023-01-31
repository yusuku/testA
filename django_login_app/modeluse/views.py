from django.shortcuts import render
from django.views.generic import TemplateView #テンプレートタグ
from .forms import AccountForm, AddAccountForm #ユーザーアカウントフォーム

# ログイン・ログアウト処理に利用
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required



#ログイン
def Login(request):
    # POST
    if request.method == 'POST':
        # フォーム入力のユーザーID・パスワード取得
        ID = request.POST.get('userid')
        Pass = request.POST.get('password')

        # Djangoの認証機能
        user = authenticate(username=ID, password=Pass)

        # ユーザー認証
        if user:
            #ユーザーアクティベート判定
            if user.is_active:
                # ログイン
                login(request,user)
                # ホームページ遷移
                return HttpResponseRedirect(reverse('home'))
            else:
                # アカウント利用不可
                return HttpResponse("アカウントが有効ではありません")
        # ユーザー認証失敗
        else:
            return HttpResponse("ログインIDまたはパスワードが間違っています")
    # GET
    else:
        return render(request, 'modeluse/login.html')


#ログアウト
@login_required
def Logout(request):
    logout(request)
    # ログイン画面遷移
    return HttpResponseRedirect(reverse('Login'))


from .forms import uploadForm ,SelectForm
from .models import NiftyFile

#ホーム
@login_required
def home(request):
    params = {
                "UserID":request.user,
                'uploadform':uploadForm(),
                'selectform':SelectForm(request.user),
            }
    
    if (request.method == 'POST'):
        params['uploadform'] = uploadForm(request.POST,request.FILES)
        niftyfile=params['uploadform'].save(commit=False)
        niftyfile.user=request.user
        
        #print(niftyfile.file.name)
        
        search=True    
        for i in niftyfile.user.niftyfile_set.all():
           #S print(i.file.name.split('/')[1])
            if i.file.name.split('/')[1]==niftyfile.file.name:
                search=False
        if search:
            niftyfile.save()
            saveObjFiles(niftyfile)
        
        params['selectform'] = SelectForm(request.user)
    
    if (request.method == 'GET'):  
        params['selectform'] = SelectForm(request.user,request.GET)
        
        
        fileid=request.GET.get('upfiles')
        
        if fileid != None and request.user != None:
            account=Account.objects.get(user=request.user)
            print(account)
            account.ObjsUrls=""
            current_host=request._current_scheme_host
            print(current_host)
            for objfile in NiftyFile.objects.get(id=fileid).objfile_set.all():
                account.ObjsUrls+=current_host+"/media/"+objfile.file.name+"\n"
                print(objfile.file.name)
            account.save()
    return render(request, "modeluse/home.html",context=params)


import numpy as np
import nibabel as nib
from skimage import measure
from django.conf import settings
from .models import ObjFile
from pathlib import Path
import os
from scipy.ndimage import zoom
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
# staticフォルダへの絶対パスを定義

atlaspath="modeluse/static/modeluse/Atlasmodel/AAL3v1_1mm.nii.gz"
atlasdata=nib.load(atlaspath)
atlasarray=atlasdata.get_fdata()


def saveObjFiles(niftyfile):
    
    fdata=nib.load(niftyfile.file.url[1:])
    farray=fdata.get_fdata()
    new_array = zoom(farray, (atlasarray.shape[0]/farray.shape[0],atlasarray.shape[1]/farray.shape[1],atlasarray.shape[2]/farray.shape[2]))
    #prepare datasets
    dataarray={}

    objindex=0

    for i in range(int(np.amax(atlasarray))):
        if i==0 or np.count_nonzero(atlasarray==i)==0:
            continue 
        tespointarray=np.where(atlasarray==i,new_array,0)
    #voxel datas to obj file
           
        verts,faces,normals,values=measure.marching_cubes(tespointarray)
        
        faces=faces+1
        
        
        filepath=""
        for j in niftyfile.file.url.split('/')[:-1]:
            filepath+=j
            if j!="":
                filepath+="/"
        
        
        filepath+="{0}_{1}.obj".format(objindex,niftyfile.file.url.split('/')[-1].split('.')[0])
        objindex+=1

        thefile=open(filepath,'w')

        for item in verts:
            thefile.write("v {0} {1} {2}\n".format(item[0],item[1],item[2]))
            
        for item in normals:
            thefile.write("vn {0} {1} {2}\n".format(item[0],item[1],item[2]))
            
        for item in faces:
            thefile.write("f {0}//{0} {1}//{1} {2}//{2}\n".format(item[0],item[1],item[2]))  
        
        fileTopath=""
        for j in filepath.split('/'):
            if j=="media": continue
            fileTopath+=j+"/"
        print (fileTopath[:-1])
            
        ObjFile(file=fileTopath[:-1],niftyfile=niftyfile).save()
        thefile.close()





#新規登録
class  AccountRegistration(TemplateView):

    def __init__(self):
        self.params = {
        "AccountCreate":False,
        "account_form": AccountForm(),
        "add_account_form":AddAccountForm(),
        }

    #Get処理
    def get(self,request):
        self.params["account_form"] = AccountForm()
        self.params["add_account_form"] = AddAccountForm()
        self.params["AccountCreate"] = False
        return render(request,"modeluse/register.html",context=self.params)

    #Post処理
    def post(self,request):
        self.params["account_form"] = AccountForm(data=request.POST)
        

        #フォーム入力の有効検証
        if self.params["account_form"].is_valid() :
            account = self.params["account_form"].save()
            # パスワードをハッシュ化
            account.set_password(account.password)

            
            # ハッシュ化パスワード更新
            account.save()

            
            # 下記追加情報
            # 下記操作のため、コミットなし
            add_account = self.params["add_account_form"].save(commit=False)
            # AccountForm & AddAccountForm 1vs1 紐付け
            add_account.user = account

                        # モデル保存
            add_account.save()
            # アカウント作成情報更新
            self.params["AccountCreate"] = True

        else:
            # フォームが有効でない場合
            print(self.params["account_form"].errors)

        return render(request,"modeluse/register.html",context=self.params)

from .models import Account

def userObjfiles(request, name, paswds):
        result=""
    
        # フォーム入力のユーザーID・パスワード取得
        ID = name
        Pass = paswds

        # Djangoの認証機能
        user = authenticate(username=ID, password=Pass)

        # ユーザー認証
        if user:
            #ユーザーアクティベート判定
            if user.is_active:
                # ログイン
                login(request,user)
                # ホームページ遷移
                
                result=Account.objects.get(user=user).ObjsUrls
                return HttpResponse(result)
            else:
                # アカウント利用不可
                return HttpResponse("アカウントが有効ではありません")
        # ユーザー認証失敗
        else:
            return HttpResponse("Failed")
        
        return HttpResponse(result)
    