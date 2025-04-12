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

print("Cobining CSVs...")

deauths = [
    # "../Downloads/awid-csv/CSV/1.Deauth/Deauth_0.csv",
    # "../Downloads/awid-csv/CSV/1.Deauth/Deauth_1.csv",
    # "../Downloads/awid-csv/CSV/1.Deauth/Deauth_2.csv",
    # "../Downloads/awid-csv/CSV/1.Deauth/Deauth_3.csv",
    # "../Downloads/awid-csv/CSV/1.Deauth/Deauth_4.csv",
    # "../Downloads/awid-csv/CSV/1.Deauth/Deauth_5.csv",
    # "../Downloads/awid-csv/CSV/1.Deauth/Deauth_6.csv",
    # "../Downloads/awid-csv/CSV/1.Deauth/Deauth_7.csv",
    # "../Downloads/awid-csv/CSV/1.Deauth/Deauth_8.csv",
    # "../Downloads/awid-csv/CSV/1.Deauth/Deauth_9.csv",
    # "../Downloads/awid-csv/CSV/1.Deauth/Deauth_10.csv",
    # "../Downloads/awid-csv/CSV/1.Deauth/Deauth_11.csv",
    # "../Downloads/awid-csv/CSV/1.Deauth/Deauth_12.csv",
    # "../Downloads/awid-csv/CSV/1.Deauth/Deauth_13.csv",
    # "../Downloads/awid-csv/CSV/1.Deauth/Deauth_14.csv",
    # "../Downloads/awid-csv/CSV/1.Deauth/Deauth_15.csv",
    # "../Downloads/awid-csv/CSV/1.Deauth/Deauth_16.csv",
    # "../Downloads/awid-csv/CSV/1.Deauth/Deauth_17.csv",
    # "../Downloads/awid-csv/CSV/1.Deauth/Deauth_18.csv",
    "../Downloads/awid-csv/CSV/1.Deauth/Deauth_19.csv",
    "../Downloads/awid-csv/CSV/1.Deauth/Deauth_20.csv",
    "../Downloads/awid-csv/CSV/1.Deauth/Deauth_21.csv",
    "../Downloads/awid-csv/CSV/1.Deauth/Deauth_22.csv",
    "../Downloads/awid-csv/CSV/1.Deauth/Deauth_23.csv",
    "../Downloads/awid-csv/CSV/1.Deauth/Deauth_24.csv",
    "../Downloads/awid-csv/CSV/1.Deauth/Deauth_25.csv",
    "../Downloads/awid-csv/CSV/1.Deauth/Deauth_26.csv",
    "../Downloads/awid-csv/CSV/1.Deauth/Deauth_27.csv",
    "../Downloads/awid-csv/CSV/1.Deauth/Deauth_28.csv",
    "../Downloads/awid-csv/CSV/1.Deauth/Deauth_29.csv",
    "../Downloads/awid-csv/CSV/1.Deauth/Deauth_30.csv",
]

disas = [
    # "../Downloads/awid-csv/CSV/2.Disas/Disas_0.csv",
    # "../Downloads/awid-csv/CSV/2.Disas/Disas_1.csv",
    "../Downloads/awid-csv/CSV/2.Disas/Disas_2.csv",
    "../Downloads/awid-csv/CSV/2.Disas/Disas_3.csv",
    "../Downloads/awid-csv/CSV/2.Disas/Disas_4.csv",
    # "../Downloads/awid-csv/CSV/2.Disas/Disas_28.csv",
    # "../Downloads/awid-csv/CSV/2.Disas/Disas_29.csv",
    "../Downloads/awid-csv/CSV/2.Disas/Disas_30.csv",
    "../Downloads/awid-csv/CSV/2.Disas/Disas_31.csv",
    "../Downloads/awid-csv/CSV/2.Disas/Disas_32.csv",
]

reassoc = [
    # "../Downloads/awid-csv/CSV/3.(Re)Assoc/(Re)Assoc_0.csv",
    # "../Downloads/awid-csv/CSV/3.(Re)Assoc/(Re)Assoc_1.csv",
    "../Downloads/awid-csv/CSV/3.(Re)Assoc/(Re)Assoc_2.csv",
    "../Downloads/awid-csv/CSV/3.(Re)Assoc/(Re)Assoc_3.csv",
    "../Downloads/awid-csv/CSV/3.(Re)Assoc/(Re)Assoc_4.csv",
    # "../Downloads/awid-csv/CSV/3.(Re)Assoc/(Re)Assoc_22.csv",
    # "../Downloads/awid-csv/CSV/3.(Re)Assoc/(Re)Assoc_23.csv",
    "../Downloads/awid-csv/CSV/3.(Re)Assoc/(Re)Assoc_24.csv",
    "../Downloads/awid-csv/CSV/3.(Re)Assoc/(Re)Assoc_25.csv",
    "../Downloads/awid-csv/CSV/3.(Re)Assoc/(Re)Assoc_26.csv",
]

rouge = [
    # "../Downloads/awid-csv/CSV/4.Rogue_AP/RogueAP_0.csv",
    # "../Downloads/awid-csv/CSV/4.Rogue_AP/RogueAP_1.csv",
    "../Downloads/awid-csv/CSV/4.Rogue_AP/RogueAP_2.csv",
    "../Downloads/awid-csv/CSV/4.Rogue_AP/RogueAP_3.csv",
    "../Downloads/awid-csv/CSV/4.Rogue_AP/RogueAP_4.csv",
    # "../Downloads/awid-csv/CSV/4.Rogue_AP/RogueAP_23.csv",
    # "../Downloads/awid-csv/CSV/4.Rogue_AP/RogueAP_24.csv",
    "../Downloads/awid-csv/CSV/4.Rogue_AP/RogueAP_25.csv",
    "../Downloads/awid-csv/CSV/4.Rogue_AP/RogueAP_26.csv",
    "../Downloads/awid-csv/CSV/4.Rogue_AP/RogueAP_27.csv",
]

files = []
files.extend(deauths)
# files.extend(disas)
# files.extend(reassoc)
# files.extend(rouge)


combined_df = pd.concat((pd.read_csv(f, sep=",", low_memory=False) for f in files), ignore_index=True)
print("Finished combining CSVs")
print(f"Combined Shape: {combined_df.shape}\n")

# 802.11 Only columns
cols = [
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

df = combined_df[cols]
print(f"Column Trimmed Shape: {df.shape}\n")

print("Distribution of Labels")
print(df["Label"].value_counts(normalize=True))
print("\n")

columns_with_missing_data = df.columns[df.isnull().mean() >= 0.5]
df = df.drop(columns_with_missing_data, axis=1)
df =df.replace("?", 0)

print(f"Column Dropped Shaped: {df.shape}\n")

df =df.dropna()

print(f"Null Rows dropped: {df.shape}\n")


# columns = ['frame.encap_type', 'frame.len', 'frame.number', 'frame.time_delta',
#        'radiotap.channel.flags.cck', 'radiotap.channel.flags.ofdm',
#        'radiotap.channel.freq', 'radiotap.datarate', 'radiotap.length',
#        'radiotap.mactime', 'radiotap.timestamp.ts', 'wlan.duration',
#        'wlan.fc.frag', 'wlan.fc.order', 'wlan.fc.moredata',
#        'wlan.fc.protected', 'wlan.fc.pwrmgt', 'wlan.fc.type', 'wlan.fc.retry',
#        'wlan.fc.subtype', 'wlan_radio.duration']

columns = ['frame.len', 'frame.number', 'frame.time_delta',
       'radiotap.channel.flags.cck', 'radiotap.channel.flags.ofdm',
       'radiotap.channel.freq', 'radiotap.length', 'wlan.duration',
       'wlan.fc.frag', 'wlan.fc.order', 'wlan.fc.moredata',
       'wlan.fc.protected', 'wlan.fc.pwrmgt', 'wlan.fc.type', 'wlan.fc.retry',
       'wlan.fc.subtype']
# columns = ["wlan.fc.type", "wlan.fc.subtype"]


X_scaled = df[columns]
y = df["Label"]

print(f"Numerical Only Columns Shape: {X_scaled.shape}\n")


print(X_scaled.head())


# # A important bit of preprocessing data is to normalize our data. Each field in our data set has some range of data. However,
# # If one numerical field only has a range of 1-2, while another field has a range of 1-1000, the latter field will inadvertnly
# # affect the AI much more. Thus, we normalize our data to all be between 0 and 1 to remove bias.
#
# # ----- AI Training -------
#
# # This splits our data into quadrants:
# # 80% of the data and labels (X_train, y_train), will be used to train the AI
# # 20% of the data and labes (X_test, y_test), will be used to test the AI after it has been trained
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

rfc = RandomForestClassifier(n_estimators=100, max_depth=None, class_weight="balanced", random_state=42)

print("Trying AI...\n")
rfc.fit(X_train, y_train)

print("Predicting with Training data with AI...\n")
y_pred = rfc.predict(X_test)

print("Confusuion Matrix:\n", confusion_matrix(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred))

importances = rfc.feature_importances_
feature_names = X_scaled.columns

idf = pd.DataFrame({
    "Feature": feature_names,
    "Importance": importances
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
