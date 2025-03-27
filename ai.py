from sklearn.datasets import fetch_kddcup99
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from pickle import dump
import pandas as pd

# ----- Get Data --------

# Fetches the KDD CUP 99 dataset 
kdd = fetch_kddcup99(shuffle=True, as_frame=True)

# Accesses the Pandas DataFrame structure
df = kdd.frame

# ---- Preprocessing of Data ------

# The dataset contains categorical data, e.g., what service the packet is "HTTP", "ICMP", etc...
# This text can't easily be used to train the AI, thus we convert these labels to IDs: 1, 2, 3, etc...
categorical_columns = ["protocol_type", "service", "flag", "labels"]

# Loop through our columns
for column in categorical_columns:
    labelEncoder = LabelEncoder()

    # This changes the column to the generated ID'd column
    df[column] = labelEncoder.fit_transform(df[column])

# Seperate the "labels" column from the dataset: the Labels column labels whether a particular packet is malicious or not
# It would be a bit silly to give our AI access to this information
X = df.drop(columns="labels")
y = df["labels"]

# A important bit of preprocessing data is to normalize our data. Each field in our data set has some range of data. However,
# If one numerical field only has a range of 1-2, while another field has a range of 1-1000, the latter field will inadvertnly
# affect the AI much more. Thus, we normalize our data to all be between 0 and 1 to remove bias.
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# ----- AI Training -------

# This splits our data into quadrants:
# 80% of the data and labels (X_train, y_train), will be used to train the AI
# 20% of the data and labes (X_test, y_test), will be used to test the AI after it has been trained
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

# Creates the SVM model
model = SVC(kernel="linear")

# Trains the AI on our train data
model.fit(X_train, y_train)

# Use our left over test data to qualify the AI's accuracy
y_prediction = model.predict(X_test)

# Computes our accuracy by comparing our predicted labels and our actual (y_test) labels
print(f"Accuracy: {accuracy_score(y_test, y_prediction)}")

# ------ Posttraining -------

print("Saving model to file...")

# Save our model to our models/ directory using the "pickle" module,
# Which can write binary data to a file
with open("./models/model.pkl", "wb") as file:
    dump(model, file)

print("Wrote model to file.")
