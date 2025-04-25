import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import itertools
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import pickle

# -------------------------------
# 1. Read the CSV and Select Columns
# -------------------------------
# Replace 'your_dataset.csv' with your actual file path.
df = pd.read_csv("train_dataset.csv")

# Keep only the relevant columns: Revenue, Net Income, and EBITDA.
df = df[['Revenue', 'Net Income', 'EBITDA']]

# -------------------------------
# 2. Generate the Recommendation Column
# -------------------------------
# Define the function for generating recommendations based on EBITDA margin.
def assign_recommendation(margin):
    if margin > 0.3:
        return "Invest"
    elif margin >= 0.15:
        return "Hold"
    else:
        return "Divest"

# Calculate EBITDA margin using Revenue and EBITDA.
df['EBITDA_margin'] = df['EBITDA'] / df['Revenue']

# Apply the function to generate the recommendation.
df['Recommendation'] = df['EBITDA_margin'].apply(assign_recommendation)

print("Dataset Sample with Recommendation:")
print(df.head())

# -------------------------------
# 3. Data Preparation
# -------------------------------
# Use Revenue, Net Income, and EBITDA as features.
X = df[['Revenue', 'Net Income', 'EBITDA']]
y = df['Recommendation']

# Encode the target labels.
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

# Scale the features to improve model performance.
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Split the dataset into training and testing sets.
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y_encoded, test_size=0.2, random_state=42)

# -------------------------------
# 4. Model Training and Evaluation
# -------------------------------
# Define the models to be trained.
models = {
    'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
    'Decision Tree': DecisionTreeClassifier(random_state=42),
    'Random Forest': RandomForestClassifier(random_state=42),
    'SVM': SVC(random_state=42)
}

results = {}

# Train each model and evaluate its performance.
for model_name, model in models.items():
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    results[model_name] = {
        'accuracy': acc,
        'classification_report': classification_report(y_test, y_pred, target_names=label_encoder.classes_)
    }
    print(f"--- {model_name} ---")
    print("Accuracy:", acc)
    print("Classification Report:\n", results[model_name]['classification_report'])
    print("\n")

# -------------------------------
# 5. Visualizing Model Performance
# -------------------------------
# 5.1 Bar Chart for Model Accuracies
model_names = list(results.keys())
accuracies = [results[model]['accuracy'] for model in model_names]

plt.figure(figsize=(8, 6))
plt.bar(model_names, accuracies, color='skyblue')
plt.xlabel('Model')
plt.ylabel('Accuracy')
plt.title('Model Accuracy Comparison')
plt.ylim(0, 1)
for i, acc in enumerate(accuracies):
    plt.text(i, acc + 0.01, f'{acc:.2f}', ha='center')
plt.tight_layout()
plt.show()

# 5.2 Confusion Matrices for Each Model
for model_name, model in models.items():
    y_pred = model.predict(X_test)
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(6, 5))
    plt.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
    plt.title(f'Confusion Matrix: {model_name}')
    plt.colorbar()
    tick_marks = np.arange(len(label_encoder.classes_))
    plt.xticks(tick_marks, label_encoder.classes_, rotation=45)
    plt.yticks(tick_marks, label_encoder.classes_)
    thresh = cm.max() / 2.0
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, format(cm[i, j], 'd'),
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")
    plt.ylabel('True label')
    plt.xlabel('Predicted label')
    plt.tight_layout()
    plt.show()

# -------------------------------
# 6. Select and Save the Best Model
# -------------------------------
# Determine the best model based on accuracy.
best_model_name = max(results, key=lambda name: results[name]['accuracy'])
best_model = models[best_model_name]
print(f"The best model is: {best_model_name} with accuracy {results[best_model_name]['accuracy']}.")

# Save the best model, along with the scaler and label encoder.
model_filename = 'best_financial_model.pkl'
with open(model_filename, 'wb') as file:
    pickle.dump({
        'model': best_model,
        'scaler': scaler,
        'label_encoder': label_encoder
    }, file)

print(f"Best model saved to {model_filename}.")
