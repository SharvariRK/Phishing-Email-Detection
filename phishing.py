import pandas as pd
#from featureExtraction import *

legitimate_urls = pd.read_csv("legitimate-urls.csv")
phishing_urls = pd.read_csv("phishing-urls.csv")

urls = legitimate_urls.append(phishing_urls)

urls = urls.drop(urls.columns[[0,3,5]],axis=1)

urls = urls.sample(frac=1).reset_index(drop=True)

urls_without_labels = urls.drop('label',axis=1)

labels = urls['label']

from sklearn.model_selection import train_test_split
data_train, data_test, labels_train, labels_test = train_test_split(urls_without_labels, labels, test_size=0.20, random_state=100)

print(len(data_train),len(data_test),len(labels_train),len(labels_test))

from sklearn.tree import DecisionTreeClassifier
model = DecisionTreeClassifier()
model.fit(data_train,labels_train)

pred_label = model.predict(data_test)

from sklearn.metrics import confusion_matrix,accuracy_score
cm = confusion_matrix(labels_test,pred_label)
print(cm)
print(accuracy_score(labels_test,pred_label))

def testPhishing(url):
    url = extractFeat(url)
    url = [url[1]]+[url[2]]+[url[4]]+url[6:]
    print(urls)
    pred = model.predict([url])
    pred = 'Phishing' if pred[0]==1 else 'Legitimate'
    return pred



