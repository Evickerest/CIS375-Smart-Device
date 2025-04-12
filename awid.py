import pandas as pd
import numpy as np
import glob
from sklearn.datasets import fetch_kddcup99
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.utils import shuffle
from pickle import dump
import pandas as pd

pd.set_option("display.max_rows", None)

# 802.11 Only columns
dot11Columns = [
    "frame.encap_type", "frame.len", "frame.number", "frame.time", "frame.time_delta", "frame.time_delta_displayed", "frame.time_epoch",
    "frame.time_relative", "radiotap.channel.flags.cck", "radiotap.channel.flags.ofdm", "radiotap.channel.freq", "radiotap.datarate",
    "radiotap.dbm_antsignal", "radiotap.length", "radiotap.mactime", "radiotap.present.tsft", "radiotap.rxflags", "radiotap.timestamp.ts",
    "radiotap.vendor_oui", "wlan.duration", "wlan.analysis.kck", "wlan.analysis.kek", "wlan.bssid", "wlan.country_info.fnm", "wlan.country_info.code",
    "wlan.da", "wlan.fc.ds", "wlan.fc.frag", "wlan.fc.order", "wlan.fc.moredata", "wlan.fc.protected", "wlan.fc.pwrmgt", "wlan.fc.type",
    "wlan.fc.retry", "wlan.fc.subtype", "wlan.fcs.bad_checksum", "wlan.fixed.beacon", "wlan.fixed.capabilities.ess", "wlan.fixed.capabilities.ibss",
    "wlan.fixed.reason_code", "wlan.fixed.timestamp", "wlan.ra", "wlan_radio.duration", "wlan.rsn.ie.gtk.key", "wlan.rsn.ie.igtk.key",
    "wlan.rsn.ie.pmkid", "wlan.sa", "wlan.seq", "wlan.ssid", "wlan.ta", "wlan.tag", "wlan.tag.length", "wlan_radio.channel", "wlan_radio.data_rate",
    "wlan_radio.end_tsf", "wlan_radio.frequency", "wlan_radio.signal_dbm", "wlan_radio.start_tsf", "wlan_radio.phy", "wlan_radio.timestamp", "wlan.rsn.capabilities.mfpc",
    "wlan_rsna_eapol.keydes.msgnr", "wlan_rsna_eapol.keydes.data", "wlan_rsna_eapol.keydes.data_len", "wlan_rsna_eapol.keydes.key_info.key_mic", "wlan_rsna_eapol.keydes.nonce",
    "eapol.keydes.key_len", "eapol.keydes.replay_counter", "eapol.len", "eapol.type", "Label"
]



deauths = [f"../Downloads/awid-csv/CSV/1.Deauth/Deauth_{i}.csv" for i in (19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30)]
disas = [f"../Downloads/awid-csv/CSV/2.Disas/Disas_{i}.csv" for i in (0, 1, 2, 3, 4, 30, 31, 34, 35, 36)]
reassoc = [f"../Downloads/awid-csv/CSV/3.(Re)Assoc/(Re)Assoc_{i}.csv" for i in (0, 1, 2, 3, 4, 30, 31, 34, 35, 36)]
rogue = [f"../Downloads/awid-csv/CSV/4.Rogue_AP/Rogue_{i}.csv" for i in (0, 1, 2, 3, 4, 30, 31, 34, 35, 36)]

files = deauths + disas


print("Combining CSVs...\n")

# Load all of the CSVs and combine them into one DataFrame
# Only read in the dot11 related columns
df = pd.concat((pd.read_csv(f, sep=",", low_memory=False, usecols=dot11Columns) for f in files), ignore_index=True)

print("Finished combining CSVs\n")
print(f"Combined Shape: {df.shape}\n")
print("Distribution of Labels")
print(df["Label"].value_counts(normalize=True))
print("\n")

columns_with_missing_data = df.columns[df.isnull().mean() >= 0.5]
df = df.drop(columns_with_missing_data, axis=1)
df =df.replace("?", 0)

print(f"Column Dropped Shaped: {df.shape}\n")

df =df.dropna()

print(f"Null Rows dropped: {df.shape}\n")

columns_subset = ['frame.len', 'frame.time_delta', 'radiotap.channel.flags.cck',
       'radiotap.channel.flags.ofdm', 'radiotap.channel.freq', 
       'radiotap.length', 'radiotap.rxflags', 'wlan.duration', 'wlan.fc.ds', 'wlan.fc.frag',
       'wlan.fc.order', 'wlan.fc.moredata', 'wlan.fc.protected',
       'wlan.fc.pwrmgt', 'wlan.fc.type', 'wlan.fc.retry', 'wlan.fc.subtype']

print(f"Shape: {df.shape}\n")

print("Cleaning up columns\n")
df.loc[:, "radiotap.rxflags"] = df["radiotap.rxflags"].apply(int, base=16)
df.loc[:, "wlan.fc.ds"] = df["wlan.fc.ds"].apply(int, base=16)

# categorial_columns = ["wlan.ra", "wlan.ta"]
# df = df.drop(categorial_columns, axis=1)

# # Convert MAC address into integers
# for cat in categorial_columns:
#     labelEncoder = LabelEncoder()
#     df[cat] = labelEncoder.fit_transform(df[cat])


# Split the Data
print("Splitting the columns...\n")
X = df[columns_subset]
y = df["Label"]

# Standardized the data
# scaler = StandardScaler()
# X = scaler.fit_transform(X)

print(f"Numerical Only Columns Shape: {X.shape}\n")

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

rfc = RandomForestClassifier(n_estimators=100, max_depth=None, class_weight="balanced", random_state=42)

print("Training AI...\n")
rfc.fit(X_train, y_train)

print("Predicting with Training data with AI...\n")
y_pred = rfc.predict(X_test)

print("Confusuion Matrix:\n", confusion_matrix(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred))

# Print out the features that have the most weight in the model
idf = pd.DataFrame({
    "Feature": columns_subset,
    "Importance": rfc.feature_importances_
}).sort_values(by="Importance", ascending=False)

print("Importances:\n")
print(idf)

# # ------ Posttraining -------

print("Saving model to file...")

# Save our model to our models/ directory using the "pickle" module,
# Which can write binary data to a file
with open("./models/model3.pkl", "wb") as file:
    dump(rfc, file, protocol=5)

print("Wrote model to file.")
