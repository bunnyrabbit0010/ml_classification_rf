import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import LabelEncoder
from imblearn.over_sampling import SMOTE
import joblib

def train_rf_with_smote():
    # Step 1: Load cleaned workout data
    print("Loading cleaned workout data...")
    df = pd.read_csv("../data/cleaned_workout_data.csv")
    print(df.isnull().sum())

    # Step 2: Drop unused columns and define X and y
    X = df.drop(columns=["workout_type_encoded"])  # all features already clean
    y = df["workout_type_encoded"]

    # Step 3: Train/test split before SMOTE (important)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Step 4: Apply SMOTE on training set only
    smote = SMOTE(k_neighbors=1, random_state=42)
    X_train_balanced, y_train_balanced = smote.fit_resample(X_train, y_train)

    # Step 5: Train Random Forest
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train_balanced, y_train_balanced)

    # Step 6: Predict on test set
    y_pred = model.predict(X_test)

    # Step 7: Evaluate
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))

    print("Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

    # Step 8: Save model and label encoder
    joblib.dump(model, "model_with_smote.joblib")
    # --- Load cleaned dataset
    # --- Load preprocessed CSV
    print("\nLoading cleaned workout data...")
    df = pd.read_csv("../data/cleaned_workout_data.csv")
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
    joblib.dump(model, "model_with_smote.joblib")

# --- Main Script ---
if __name__ == "__main__":
    try:
        train_rf_with_smote()
    except Exception as e:
        print(f"Script failed: {e}")