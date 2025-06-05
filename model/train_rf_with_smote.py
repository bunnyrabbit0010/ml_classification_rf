import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import LabelEncoder
from imblearn.over_sampling import SMOTE
import joblib

# --- Load cleaned dataset
# --- Load preprocessed CSV
print("\nLoading cleaned workout data...")
df = pd.read_csv("../preprocess/cleaned_workout_data.csv")
print(df.isnull().sum())


# --- Drop unused columns and define X and y
X = df.drop(columns=["workout_type_encoded"])  # all features already clean
y = df["workout_type_encoded"]

# --- Train/test split before SMOTE (important)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


# --- Apply SMOTE on training set only
smote = SMOTE(k_neighbors=1, random_state=42)
X_train_balanced, y_train_balanced = smote.fit_resample(X_train, y_train)

# --- Train Random Forest
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train_balanced, y_train_balanced)

# --- Predict on test set
y_pred = model.predict(X_test)

# --- Evaluate
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# --- Save model and label encoder
joblib.dump(model, "models/model_with_smote.joblib")

