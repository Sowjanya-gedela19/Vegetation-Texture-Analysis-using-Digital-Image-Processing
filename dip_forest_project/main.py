
import os
import numpy as np
import pandas as pd
import cv2
from skimage.feature import graycomatrix, graycoprops, local_binary_pattern
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import matplotlib

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, "dataset")
IMAGES_PATH = os.path.join(DATASET_PATH, 'images')
MASKS_PATH = os.path.join(DATASET_PATH, 'masks')
META_DATA_PATH = os.path.join(DATASET_PATH, 'meta_data.csv')
DENSITY_THRESHOLD = 0.3
IMAGE_SIZE = 256
GLCM_DISTANCES = [1, 2, 3]
GLCM_ANGLES = [0, np.pi/4, np.pi/2, 3*np.pi/4]
GLCM_PROPERTIES = ['contrast', 'energy', 'homogeneity', 'correlation']
LBP_RADIUS = 3
LBP_N_POINTS = 8 * LBP_RADIUS
EPOCHS = 50
BATCH_SIZE = 32
TEST_SIZE = 0.2
RANDOM_STATE = 42

def load_meta_data(csv_path):
    if not os.path.exists(csv_path):
        print('Warning: meta_data.csv not found.')
        return pd.DataFrame(columns=['image_filename', 'mask_filename'])
    
    with open(csv_path, 'r') as f:
        content = f.read().strip()
    if not content:
        print('Warning: meta_data.csv is empty.')
        return pd.DataFrame(columns=['image_filename', 'mask_filename'])
    df = pd.read_csv(csv_path)
    print(f'Loaded {len(df)} image-mask pairs from CSV')
    return df

def load_image(image_path):
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"ERROR: Cannot load image: {image_path}")
    return img

def load_mask(mask_path):
    mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
    if mask is None:
        raise ValueError(f"ERROR: Cannot load mask: {mask_path}")
    return mask

def compute_vegetation_density(mask):
    total_pixels = mask.size
    vegetation_pixels = np.count_nonzero(mask)
    density = vegetation_pixels / total_pixels
    return density

def label_vegetation(density, threshold=DENSITY_THRESHOLD):
    return 1 if density > threshold else 0

def convert_to_grayscale(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return gray

def extract_glcm_features(gray_image, distances=GLCM_DISTANCES, angles=GLCM_ANGLES):
    gray_quantized = (gray_image // 16).astype(np.uint8)
    glcm = graycomatrix(gray_quantized, distances=distances, angles=angles, levels=16, symmetric=True, normed=True)
    features = {}
    for prop in GLCM_PROPERTIES:
        prop_values = graycoprops(glcm, prop)
        features[prop] = np.mean(prop_values)
    return features

def extract_lbp_features(gray_image, radius=LBP_RADIUS, n_points=LBP_N_POINTS):
    lbp = local_binary_pattern(gray_image, n_points, radius, method='uniform')
    n_bins = n_points + 2
    hist, _ = np.histogram(lbp.ravel(), bins=n_bins, range=(0, n_bins), density=True)
    return hist

def extract_all_features(gray_image):
    glcm_features = extract_glcm_features(gray_image)
    lbp_features = extract_lbp_features(gray_image)
    feature_vector = np.array([glcm_features['contrast'], glcm_features['energy'], glcm_features['homogeneity'], glcm_features['correlation'], *lbp_features])
    return feature_vector

def prepare_dataset(meta_data_df, images_path, masks_path):
    features_list = []
    labels_list = []
    print('\nProcessing images...')
    for idx, row in meta_data_df.iterrows():
        image_filename = row['image_filename']
        mask_filename = row['mask_filename']
        image_path = os.path.join(images_path, image_filename)
        mask_path = os.path.join(masks_path, mask_filename)
        try:
            image = load_image(image_path)
            mask = load_mask(mask_path)
            density = compute_vegetation_density(mask)
            label = label_vegetation(density)
            gray = convert_to_grayscale(image)
            features = extract_all_features(gray)
            features_list.append(features)
            labels_list.append(label)
            label_str = 'High Vegetation (Coarse)' if label == 1 else 'Low Vegetation (Smooth)'
            print(f'  Processed {image_filename}: density={density:.3f}, label={label_str}')
        except Exception as e:
            print(f'  Error processing {image_filename}: {e}')
    X = np.array(features_list)
    y = np.array(labels_list)
    print(f'\nDataset prepared: {len(X)} samples, {X.shape[1]} features')
    print(f'Class distribution: High Vegetation (Coarse)={np.sum(y==1)}, Low Vegetation (Smooth)={np.sum(y==0)}')
    return X, y

def build_neural_network(input_dim):
    model = keras.Sequential([layers.Dense(128, activation='relu', input_shape=(input_dim,)), layers.BatchNormalization(), layers.Dropout(0.3), layers.Dense(64, activation='relu'), layers.BatchNormalization(), layers.Dropout(0.3), layers.Dense(32, activation='relu'), layers.BatchNormalization(), layers.Dropout(0.2), layers.Dense(1, activation='sigmoid')])
    model.compile(optimizer=keras.optimizers.Adam(learning_rate=0.001), loss='binary_crossentropy', metrics=['accuracy'])
    return model

def compute_class_weights(y):
    from sklearn.utils.class_weight import compute_class_weight
    classes = np.unique(y)
    weights = compute_class_weight('balanced', classes=classes, y=y)
    return dict(zip(classes, weights))

def train_model(X_train, y_train, X_val, y_val, input_dim):
    model = build_neural_network(input_dim)
    print('\nTraining Neural Network...')
    print(f'  Training samples: {len(X_train)}')
    print(f'  Validation samples: {len(X_val)}')
    print(f'  Features: {input_dim}')
    print(f'  Epochs: {EPOCHS}')
    print(f'  Batch size: {BATCH_SIZE}')
    class_weights = compute_class_weights(y_train)
    print(f'  Class weights: {class_weights}')
    early_stopping = keras.callbacks.EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
    history = model.fit(X_train, y_train, validation_data=(X_val, y_val), epochs=EPOCHS, batch_size=BATCH_SIZE, callbacks=[early_stopping], class_weight=class_weights, verbose=1)
    return model, history

def evaluate_model(model, X_test, y_test):
    y_pred_prob = model.predict(X_test)
    threshold = 0.4
    y_pred = (y_pred_prob > threshold).astype(int).flatten()
    accuracy = accuracy_score(y_test, y_pred)
    print('\n' + '='*60)
    print('MODEL EVALUATION RESULTS')
    print('='*60)
    print(f'\nAccuracy: {accuracy:.4f} ({accuracy*100:.2f}%)')
    print(f'Prediction threshold: {threshold}')
    print('\nClassification Report:')
    print('-'*60)
    report = classification_report(y_test, y_pred, target_names=['Low Vegetation (Smooth)', 'High Vegetation (Coarse)'])
    print(report)
    return accuracy, y_pred

def visualize_samples(images_path, masks_path, meta_data_df, num_samples=6):
    """Display sample images with their masks and labels."""
    print('\n' + '='*60)
    print('SAMPLE IMAGES VISUALIZATION')
    print('='*60)
    
    # Create figure
    fig, axes = plt.subplots(2, 3, figsize=(12, 8))
    fig.suptitle('Sample Satellite Images with Vegetation Masks', fontsize=14)
    
    # Select random samples
    sample_indices = np.random.choice(len(meta_data_df), num_samples, replace=False)
    
    for idx, i in enumerate(sample_indices):
        row = meta_data_df.iloc[i]
        image_path = os.path.join(images_path, row['image_filename'])
        mask_path = os.path.join(masks_path, row['mask_filename'])
        
        # Load image and mask
        image = cv2.imread(image_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
        
        # Compute density and label
        density = compute_vegetation_density(mask)
        label = 'High Vegetation (Coarse)' if density > DENSITY_THRESHOLD else 'Low Vegetation (Smooth)'
        
        # Plot
        ax = axes[idx // 3, idx % 3]
        ax.imshow(image)
        ax.imshow(mask, alpha=0.3, cmap='jet')
        ax.set_title(f'{label}\nDensity: {density:.2f}')
        ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('sample_visualization.png', dpi=150, bbox_inches='tight')
    print(f'Saved visualization to: sample_visualization.png')
    plt.show()  # Display the plot on screen
    plt.pause(5)  # Wait 5 seconds so user can see it
    plt.close()

def generate_sample_data(num_samples=100, output_path='dataset'):
    print(f'\nGenerating {num_samples} sample images and masks...')
    images_dir = os.path.join(output_path, 'images')
    masks_dir = os.path.join(output_path, 'masks')
    os.makedirs(images_dir, exist_ok=True)
    os.makedirs(masks_dir, exist_ok=True)
    meta_data = []
    for i in range(num_samples):
        # Generate balanced classes (50% high, 50% low)
        high_vegetation = i % 2 == 0
        image = np.random.randint(0, 256, (IMAGE_SIZE, IMAGE_SIZE, 3), dtype=np.uint8)
        if high_vegetation:
            noise = np.random.randint(-30, 30, (IMAGE_SIZE, IMAGE_SIZE))
            for c in range(3):
                image[:, :, c] = np.clip(image[:, :, c].astype(np.int16) + noise, 0, 255).astype(np.uint8)
            # High density mask (>0.5 to ensure > 0.3 threshold)
            mask = (np.random.random((IMAGE_SIZE, IMAGE_SIZE)) > 0.4).astype(np.uint8) * 255
        else:
            image = cv2.GaussianBlur(image, (15, 15), 0)
            # Low density mask (<0.2 to ensure < 0.3 threshold)
            mask = (np.random.random((IMAGE_SIZE, IMAGE_SIZE)) > 0.8).astype(np.uint8) * 255
        image_filename = f'image_{i:04d}.png'
        cv2.imwrite(os.path.join(images_dir, image_filename), image)
        mask_filename = f'mask_{i:04d}.png'
        cv2.imwrite(os.path.join(masks_dir, mask_filename), mask)
        meta_data.append({'image_filename': image_filename, 'mask_filename': mask_filename})
    df = pd.DataFrame(meta_data)
    csv_path = os.path.join(output_path, 'meta_data.csv')
    df.to_csv(csv_path, index=False)
    print(f'Generated {num_samples} samples')
    print(f'  Images saved to: {images_dir}')
    print(f'  Masks saved to: {masks_dir}')
    print(f'  CSV saved to: {csv_path}')

def main():
    print('='*60)
    print('Vegetation Classification from Satellite Images')
    print('='*60)
    
    # Load metadata - DO NOT generate dummy data
    # Your real dataset should already be in dataset/images/ and dataset/masks/
    meta_data = load_meta_data(META_DATA_PATH)
    
    if len(meta_data) == 0:
        print('ERROR: No data found in meta_data.csv')
        print('Please ensure your dataset is in:')
        print('  - dataset/images/ (satellite images)')
        print('  - dataset/masks/  (vegetation masks)')
        print('  - dataset/meta_data.csv (mapping file)')
        return
    
    # Verify dataset structure
    print(f'\nChecking dataset structure...')
    print(f'  Images folder: {IMAGES_PATH}')
    print(f'  Masks folder: {MASKS_PATH}')
    print(f'  CSV file: {META_DATA_PATH}')
    
    # Check if folders exist
    if not os.path.exists(IMAGES_PATH):
        print(f'ERROR: Images folder not found: {IMAGES_PATH}')
        return
    if not os.path.exists(MASKS_PATH):
        print(f'ERROR: Masks folder not found: {MASKS_PATH}')
        return
    
    # Count actual files
    image_files = [f for f in os.listdir(IMAGES_PATH) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    mask_files = [f for f in os.listdir(MASKS_PATH) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    print(f'  Found {len(image_files)} images')
    print(f'  Found {len(mask_files)} masks')
    
    if len(image_files) == 0:
        print('ERROR: No image files found in dataset/images/')
        return
    
    X, y = prepare_dataset(meta_data, IMAGES_PATH, MASKS_PATH)
    
    # Visualize sample images
    visualize_samples(IMAGES_PATH, MASKS_PATH, meta_data)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y)
    X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y_train)
    print(f'\nData split:')
    print(f'  Training: {len(X_train)} samples')
    print(f'  Validation: {len(X_val)} samples')
    print(f'  Test: {len(X_test)} samples')
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)
    X_test_scaled = scaler.transform(X_test)
    model, history = train_model(X_train_scaled, y_train, X_val_scaled, y_val, X_train.shape[1])
    accuracy, y_pred = evaluate_model(model, X_test_scaled, y_test)
    
    # Visualize predictions on test samples
    visualize_predictions(model, X_test_scaled, y_test, meta_data, IMAGES_PATH, MASKS_PATH, scaler)
    
    print('\n' + '='*60)
    print('Pipeline completed successfully!')
    print('='*60)
    return model, accuracy

def visualize_predictions(model, X_test, y_test, meta_data_df, images_path, masks_path, scaler):
    """Display test images with their predicted labels."""
    print('\n' + '='*60)
    print('PREDICTION RESULTS ON TEST SAMPLES')
    print('='*60)
    
    # Get predictions
    y_pred_prob = model.predict(X_test)
    threshold = 0.4
    y_pred = (y_pred_prob > threshold).astype(int).flatten()
    
    # Create figure
    fig, axes = plt.subplots(2, 5, figsize=(15, 6))
    fig.suptitle('Neural Network Predictions on Test Samples', fontsize=14)
    
    # Get test indices (last 20 samples based on split)
    test_indices = list(range(len(meta_data_df) - len(y_test), len(meta_data_df)))
    
    for idx in range(min(10, len(y_test))):
        row = meta_data_df.iloc[test_indices[idx]]
        image_path = os.path.join(images_path, row['image_filename'])
        
        # Load image
        image = cv2.imread(image_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Get prediction
        pred_label = 'Predicted: High Vegetation (Coarse)' if y_pred[idx] == 1 else 'Predicted: Low Vegetation (Smooth)'
        true_label = 'True: High Vegetation (Coarse)' if y_test[idx] == 1 else 'True: Low Vegetation (Smooth)'
        
        # Plot
        ax = axes[idx // 5, idx % 5]
        ax.imshow(image)
        ax.set_title(f'{pred_label}\n{true_label}', fontsize=10)
        ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('prediction_visualization.png', dpi=150, bbox_inches='tight')
    print(f'Saved prediction visualization to: prediction_visualization.png')
    plt.show()
    plt.pause(5)
    plt.close()

if __name__ == '__main__':
    main()
