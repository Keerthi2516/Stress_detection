
from django.db.models import  Count, Avg
from django.shortcuts import render, redirect
from django.db.models import Count
from django.db.models import Q
import datetime
import xlwt
from django.http import HttpResponse


import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.metrics import accuracy_score
from sklearn.tree import DecisionTreeClassifier

# Create your views here.
from Remote_User.models import ClientRegister_Model,predict_stress_detection,detection_ratio,detection_accuracy


def serviceproviderlogin(request):
    if request.method  == "POST":
        admin = request.POST.get('username')
        password = request.POST.get('password')
        if admin == "Admin" and password =="Admin":
            detection_accuracy.objects.all().delete()
            return redirect('View_Remote_Users')

    return render(request,'SProvider/serviceproviderlogin.html')

def View_Prediction_Of_Stress_Detection_Status_Ratio(request):
    detection_ratio.objects.all().delete()
    ratio = ""
    kword = 'Stress Not Found'
    print(kword)
    obj = predict_stress_detection.objects.all().filter(Q(Prediction=kword))
    obj1 = predict_stress_detection.objects.all()
    count = obj.count();
    count1 = obj1.count();
    ratio = (count / count1) * 100
    if ratio != 0:
        detection_ratio.objects.create(names=kword, ratio=ratio)

    ratio12 = ""
    kword12 = 'Stress Found'
    print(kword12)
    obj12 = predict_stress_detection.objects.all().filter(Q(Prediction=kword12))
    obj112 = predict_stress_detection.objects.all()
    count12 = obj12.count();
    count112 = obj112.count();
    ratio12 = (count12 / count112) * 100
    if ratio12 != 0:
        detection_ratio.objects.create(names=kword12, ratio=ratio12)


    obj = detection_ratio.objects.all()
    return render(request, 'SProvider/View_Prediction_Of_Stress_Detection_Status_Ratio.html', {'objs': obj})

def View_Remote_Users(request):
    obj=ClientRegister_Model.objects.all()
    return render(request,'SProvider/View_Remote_Users.html',{'objects':obj})

def charts(request,chart_type):
    chart1 = detection_ratio.objects.values('names').annotate(dcount=Avg('ratio'))
    return render(request,"SProvider/charts.html", {'form':chart1, 'chart_type':chart_type})

def charts1(request,chart_type):
    chart1 = detection_accuracy.objects.values('names').annotate(dcount=Avg('ratio'))
    return render(request,"SProvider/charts1.html", {'form':chart1, 'chart_type':chart_type})

def View_Prediction_Of_Stress_Detection_Status(request):
    obj =predict_stress_detection.objects.all()
    return render(request, 'SProvider/View_Prediction_Of_Stress_Detection_Status.html', {'list_objects': obj})

def likeschart(request,like_chart):
    charts =detection_accuracy.objects.values('names').annotate(dcount=Avg('ratio'))
    return render(request,"SProvider/likeschart.html", {'form':charts, 'like_chart':like_chart})


def Download_Trained_DataSets(request):

    response = HttpResponse(content_type='application/ms-excel')
    # decide file name
    response['Content-Disposition'] = 'attachment; filename="Predicted_Datasets.xls"'
    # creating workbook
    wb = xlwt.Workbook(encoding='utf-8')
    # adding sheet
    ws = wb.add_sheet("sheet1")
    # Sheet header, first row
    row_num = 0
    font_style = xlwt.XFStyle()
    # headers are bold
    font_style.font.bold = True
    # writer = csv.writer(response)
    obj = predict_stress_detection.objects.all()
    data = obj  # dummy method to fetch data.
    for my_row in data:
        row_num = row_num + 1

        ws.write(row_num, 0, my_row.Patient_ID, font_style)
        ws.write(row_num, 1, my_row.Age, font_style)
        ws.write(row_num, 2, my_row.Sex, font_style)
        ws.write(row_num, 3, my_row.Cholesterol, font_style)
        ws.write(row_num, 4, my_row.Blood_Pressure, font_style)
        ws.write(row_num, 5, my_row.Heart_Rate, font_style)
        ws.write(row_num, 6, my_row.Diabetes, font_style)
        ws.write(row_num, 7, my_row.Family_History, font_style)
        ws.write(row_num, 8, my_row.Smoking, font_style)
        ws.write(row_num, 9, my_row.Obesity, font_style)
        ws.write(row_num, 10, my_row.Alcohol_Consumption, font_style)
        ws.write(row_num, 11, my_row.Exercise_Hours_Per_Week, font_style)
        ws.write(row_num, 12, my_row.Diet, font_style)
        ws.write(row_num, 13, my_row.Previous_Heart_Problems, font_style)
        ws.write(row_num, 14, my_row.Medication_Use, font_style)
        ws.write(row_num, 15, my_row.Stress_Level, font_style)
        ws.write(row_num, 16, my_row.Sedentary_Hours_Per_Day, font_style)
        ws.write(row_num, 17, my_row.Income, font_style)
        ws.write(row_num, 18, my_row.BMI, font_style)
        ws.write(row_num, 19, my_row.Triglycerides, font_style)
        ws.write(row_num, 20, my_row.Physical_Activity_Days_Per_Week, font_style)
        ws.write(row_num, 21, my_row.Sleep_Hours_Per_Day, font_style)
        ws.write(row_num, 22, my_row.Country, font_style)
        ws.write(row_num, 23, my_row.Continent, font_style)
        ws.write(row_num, 24, my_row.Hemisphere, font_style)
        ws.write(row_num, 25, my_row.Heart_Attack, font_style)
        ws.write(row_num, 26, my_row.Prediction, font_style)

    wb.save(response)
    return response

def train_model(request):
    detection_accuracy.objects.all().delete()

    df = pd.read_csv('Datasets.csv')

    def apply_response(Label):
        if (Label == 0):
            return 0  # Stress Not Found
        elif (Label == 1):
            return 1 # Stress Found

    df['results'] = df['Label'].apply(apply_response)

    cv = CountVectorizer()
    X = df['Patient_ID']
    y = df['results']

    print("Patient_ID")
    print(X)
    print("Results")
    print(y)

    cv = CountVectorizer()
    X = cv.fit_transform(X)

    models = []
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20)
    X_train.shape, X_test.shape, y_train.shape

    # SVM Model
    print("SVM")
    from sklearn import svm
    lin_clf = svm.LinearSVC()
    lin_clf.fit(X_train, y_train)
    predict_svm = lin_clf.predict(X_test)
    svm_acc = accuracy_score(y_test, predict_svm) * 100
    print(svm_acc)
    print("CLASSIFICATION REPORT")
    print(classification_report(y_test, predict_svm))
    print("CONFUSION MATRIX")
    print(confusion_matrix(y_test, predict_svm))
    models.append(('svm', lin_clf))
    detection_accuracy.objects.create(names="SVM", ratio=svm_acc)

    print("Decision Tree Classifier")
    dtc = DecisionTreeClassifier()
    dtc.fit(X_train, y_train)
    dtcpredict = dtc.predict(X_test)
    print("ACCURACY")
    print(accuracy_score(y_test, dtcpredict) * 100)
    print("CLASSIFICATION REPORT")
    print(classification_report(y_test, dtcpredict))
    print("CONFUSION MATRIX")
    print(confusion_matrix(y_test, dtcpredict))
    models.append(('DecisionTreeClassifier', dtc))
    detection_accuracy.objects.create(names="Decision Tree Classifier", ratio=accuracy_score(y_test, dtcpredict) * 100)

    print("Random Forest Classifier")
    from sklearn.ensemble import RandomForestClassifier
    rf_clf = RandomForestClassifier()
    rf_clf.fit(X_train, y_train)
    rfpredict = rf_clf.predict(X_test)
    print("ACCURACY")
    print(accuracy_score(y_test, rfpredict) * 100)
    print("CLASSIFICATION REPORT")
    print(classification_report(y_test, rfpredict))
    print("CONFUSION MATRIX")
    print(confusion_matrix(y_test, rfpredict))
    models.append(('RandomForestClassifier', rf_clf))
    detection_accuracy.objects.create(names="Random Forest Classifier", ratio=accuracy_score(y_test, rfpredict) * 100)

    print("Naive Bayes")
    from sklearn.naive_bayes import MultinomialNB
    NB = MultinomialNB()
    NB.fit(X_train, y_train)
    predict_nb = NB.predict(X_test)
    naivebayes = accuracy_score(y_test, predict_nb) * 100
    print(naivebayes)
    print(confusion_matrix(y_test, predict_nb))
    print(classification_report(y_test, predict_nb))
    models.append(('naive_bayes', NB))
    detection_accuracy.objects.create(names="Naive Bayes", ratio=naivebayes)


    csv_format = 'Results.csv'
    df.to_csv(csv_format, index=False)
    df.to_markdown

    obj = detection_accuracy.objects.all()
    return render(request,'SProvider/train_model.html', {'objs': obj})