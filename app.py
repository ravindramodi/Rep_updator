####Make sure we have Category_details -----> Excel file with proper heading for Category Updation
####Make sure we have all_brand_details ----> CSV File (No filter applied, Download complete table from Metabase)
###Befor Proceeding please check Base and Updates file name 
####Make sure repository and updates file have image_link column instead of image_url
import pandas as pd

# Load original sheet and update sheet
df_original = pd.read_excel('/Users/ravindra_modi/Documents/Elgrocer software/Rep.xlsx')
df_updates = pd.read_excel('/Users/ravindra_modi/Documents/Elgrocer software/Update.xlsx')
df_brands = pd.read_csv('/Users/ravindra_modi/Documents/Elgrocer software/all_brand_details.csv')
df_subcat = pd.read_excel('/Users/ravindra_modi/Documents/Elgrocer software/Category_details.xlsx')

# Normalizing Barcode function
def normalize_barcode(barcode):
    barcode_str = str(barcode)
    return barcode_str.zfill(13) if barcode_str.isdigit() else barcode_str

# Normalize barcodes in both dataframes
df_original['barcode'] = df_original['barcode'].apply(normalize_barcode)
df_updates['Barcode'] = df_updates['Barcode'].apply(normalize_barcode)

# Set 'Barcode' as the index for df_updates
df_updates.set_index('Barcode', inplace=True)

# Function to safely update values
def safe_update(row, col, update_col):
    try:
        update_value = df_updates.at[row['barcode'], update_col]
        return update_value if not pd.isna(update_value) else row[col]
    except KeyError:
        return row[col]

# Columns to update
columns_to_update = ['brand_id', 'name', 'unit_weight', 'size_unit', 'image_link', 'subcatid']

# Update each column
for col in columns_to_update:
    update_col = f'{col}_current_value'
    df_original[col] = df_original.apply(lambda row: safe_update(row, col, update_col), axis=1)

# Merge with brand details
df_original = pd.merge(df_original, df_brands[['ID', 'Name']], left_on='brand_id', right_on='ID', how='left')

# Update brand_name
def update_brand_name(row):
    if pd.isna(row['Name']):
        print(f"Brand_id Not Found for barcode: {row['barcode']}")
        return 'Brand name not found'
    return row['Name']

df_original['brand_name'] = df_original.apply(update_brand_name, axis=1)
df_original.drop(columns=['ID', 'Name'], inplace=True)



#print("Columns in Sub_category_details.xlsx:", df_subcat.columns)

# Perform the merge based on 'Sub Category ID' and 'subcatid'
df_original = pd.merge(
    df_original, 
    df_subcat[['Sub Category ID', 'Sub Category Name', 'Category Name']], 
    left_on='subcatid', right_on='Sub Category ID', 
    how='left'
)

# Check columns after merging
#print("Columns after merging with sub-category details:", df_original.columns)

# Update subcat_name and category_name with logging for missing values
def update_subcat_and_category_name(row):
    # Handle missing subcat_name
    if pd.isna(row['Sub Category Name']):
        print(f"Subcatid Not Found for barcode: {row['barcode']}")
        subcat_name = 'Subcategory name not found'
    else:
        subcat_name = row['Sub Category Name']
    
    # Handle missing category_name
    if pd.isna(row['Category Name']):
        print(f"Category Name Not Found for barcode: {row['barcode']}")
        category_name = 'Category name not found'
    else:
        category_name = row['Category Name']
    
    return pd.Series([subcat_name, category_name])

# Apply the update to both columns
df_original[['subcat_name', 'category_name']] = df_original.apply(update_subcat_and_category_name, axis=1)

# Drop unnecessary columns (Sub Category ID, Sub Category Name, and Category Name from the merge)
df_original.drop(columns=['Sub Category ID', 'Sub Category Name', 'Category Name'], inplace=True)


# Format size
def format_size(unit_weight, size_unit):
    try:
        # Try converting unit_weight to a float
        unit_weight = float(unit_weight)
        if unit_weight == 0:
            return size_unit
        else:
            # Format the float value
            weight_str = f"{unit_weight:.10f}".rstrip('0').rstrip('.')
            return f"{weight_str}{size_unit}"
    except ValueError:
        # If conversion to float fails, return size_unit (fallback behavior)
        print(f"Warning: unit_weight '{unit_weight}' is not a valid number.")
        print("Concat Manually if the values are correct or rework")
        return size_unit

df_original['size'] = df_original.apply(lambda row: format_size(row['unit_weight'], row['size_unit']), axis=1)

df_original = df_original.drop_duplicates()

# Save the updated DataFrame
df_original.to_excel('/Users/ravindra_modi/Documents/Elgrocer software/updated_original_sheet.xlsx', index=False)

print("Catalog update completed.")