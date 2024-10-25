import pandas as pd

# Load original sheet and update sheet
# Replace with actual file paths or use pd.read_excel() if using Excel files
df_original = pd.read_excel('/Users/ravindra_modi/Documents/Elgrocer software/Rep.xlsx')
df_updates = pd.read_excel('/Users/ravindra_modi/Documents/Elgrocer software/Update.xlsx')
df_brands = pd.read_csv('/Users/ravindra_modi/Documents/Elgrocer software/all_brand_details.csv')
df_subcat = pd.read_excel('/Users/ravindra_modi/Documents/Elgrocer software/Sub_category_details.xlsx')

# Normalizing Barcode function
def normalize_barcode(barcode):
    # Convert the barcode to string before checking
    barcode_str = str(barcode)
    if barcode_str.isdigit():
        return barcode_str.zfill(13)
    return barcode_str  # Ensure returning as string
df_original['barcode'] = df_original['barcode'].apply(normalize_barcode)

df_updates['barcode'] = df_updates['barcode'].apply(normalize_barcode)



# Loop through the relevant columns to update based on 'barcode'
columns_to_update = ['brand_id', 'name', 'unit_weight', 'size_unit', 'image_link']  # Add other columns as needed


for col in columns_to_update:
    update_col = f'{col}_current_value'  # Column name in df_updates for current values
    # Only update where df_updates has non-null values
    df_original[col] = df_original.apply(
        lambda row: row[col] if pd.isna(df_updates.set_index('Barcode').loc[row['barcode'], update_col]) 
        else df_updates.set_index('Barcode').loc[row['barcode'], update_col], axis=1
    )

# Perform the merge with brand details
df_original = pd.merge(df_original, df_brands[['ID', 'Name']], left_on='brand_id', right_on='ID', how='left')

# Step 3: Add condition to handle brand_id not found in df_brands
def update_brand_name(row):
    if pd.isna(row['Name']):
        print(f"Brand_id Not Found for barcode: {row['barcode']}")  # Print the message for missing brand_id
        return 'Brand name not found'  # Assign this value when brand_id is not found in df_brands
    return row['Name']

# Update brand_name using the above function
df_original['brand_name'] = df_original.apply(update_brand_name, axis=1)

# Drop unnecessary columns (ID and Name from the merge)
df_original.drop(columns=['ID', 'Name'], inplace=True)


# Perform the merge with sub-category details
df_original = pd.merge(df_original, df_subcat[['Sub Category ID', 'Sub Category Name']], left_on='subcatid', right_on='Sub Category ID', how='left')

# Step 6: Add condition to handle subcatid not found in df_subcat
def update_subcat_name(row):
    if pd.isna(row['Sub Category Name']):
        print(f"Subcatid Not Found for barcode: {row['barcode']}")  # Print the message for missing subcatid
        return 'Subcategory name not found'  # Assign this value when subcatid is not found in df_subcat
    return row['Sub Category Name']

# Update subcat_name using the above function
df_original['subcat_name'] = df_original.apply(update_subcat_name, axis=1)

# Drop unnecessary columns (Sub Category ID and Sub Category Name from the merge)
df_original.drop(columns=['Sub Category ID', 'Sub Category Name'], inplace=True)

# Create or update the 'Size' column based on the 'unit_weight' and 'size_unit'
def format_size(unit_weight, size_unit):
    if unit_weight == 0:
        return size_unit
    else:
        weight_str = f"{unit_weight:.10f}".rstrip('0').rstrip('.')
        return f"{weight_str}{size_unit}"

df_original['size'] = df_original.apply(lambda row: format_size(row['unit_weight'], row['size_unit']), axis=1)





# Save the updated DataFrame
df_original.to_excel('/Users/ravindra_modi/Documents/Elgrocer software/updated_original_sheet.xlsx', index=False)



