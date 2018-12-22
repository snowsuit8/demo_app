from django.shortcuts import render, redirect
from .forms import InputForm
from .models import Customers
from sklearn.externals import joblib
import numpy as np

loaded_model = joblib.load('demo_app/demo_model.pkl') #最初に読み込みを行う（参考書とかに書いていないが重要！）

def index(request):
    return render(request, 'demo_app/index.html', {})

def input_form(request):
    if request.method == 'POST':
        form = InputForm(request.POST)
        if form.is_valid():
            form.save() #入力された値を保存
            return redirect('result')
    else:
        form = InputForm()
        return render(request, 'demo_app/input_form.html', {'form':form})

def history(request):
    if request.method  == 'POST':
        d_id = request.POST
        d_customer = Customers.objects.filter(id=d_id['d_id'])
        d_customer.delete()
        customers = Customers.objects.all()
        return render(request, 'demo_app/history.html', {'customers':customers}) # 顧客データをHTMLに渡す
    else:
        customers = Customers.objects.all() # 顧客データの取得
        return render(request, 'demo_app/history.html', {'customers':customers}) # 顧客データをHTMLに渡す

def result(request):
    # DBからデータを取得
    _data = Customers.objects.order_by('id').reverse().values_list('limit_balance', 'sex',\
     'education', 'marriage', 'age', 'pay_0', 'pay_2', 'pay_3',\
      'pay_4', 'pay_5', 'pay_6', 'bill_amt_1', 'pay_amt_1', 'pay_amt_2',\
       'pay_amt_3', 'pay_amt_4', 'pay_amt_5', 'pay_amt_6')
    x = np.array([_data[0]])
    y = loaded_model.predict(x)
    y_proba = loaded_model.predict_proba(x)
    y_proba = y_proba * 100

    if y[0] == 0:
        if y_proba[0][y[0]] >= 0.75:
            comment = 'NG'
        else:
            comment = '多分NG'
    else:
        if y_proba[0][y[0]] >= 0.75:
            comment = 'OK'
        else:
            comment = '多分OK'

    # 推論結果の保存
    customer = Customers.objects.order_by('id').reverse()[0]
    customer.result = y[0]
    customer.proba = y_proba[0][y[0]]
    customer.comment = comment
    customer.save()

    return render(request, 'demo_app/result.html', {'y':y[0], 'y_proba':round(y_proba[0][y[0]], 2), 'comment':comment})
