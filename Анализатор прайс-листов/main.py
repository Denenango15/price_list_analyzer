''' Explanation.
Price list analyzer. Unloading the array in html, and also added a separate html file with the unloading of a specific product
that the user enters with the ability to add more products. After you specify, for example, "Филе",
the program will ask if an html file is needed, write yes, after the program will ask if we want to add something else, if
we write yes, we can write, for example, "pink salmon" after that we write again that we need an html file, but
nothing more do not add, write no, you will have 2 files
'''

import os
import pandas as pd


class PriceMachine():
    def __init__(self):
        self.data = pd.DataFrame(columns=['product_name', 'price', 'weight', 'file_name'])
        self.selected_products = []  # Список выбранных продуктов

    def load_prices(self, folder_path=''):
        '''
           Scans the specified directory. Searches for files with the word price in the name.
            The file searches for columns with the product name, price and weight.
             Acceptable names for the product column:
                товар
                название
                наименование
                продукт
        '''
        # A loop to iterate through the files in the specified directory.
        for file_name in os.listdir(folder_path):
            # checking files for the specified parameters
            if 'price' in file_name.lower() and file_name.endswith('.csv'):
                file_path = os.path.join(folder_path, file_name)
                # Reading data from a CSV file to a DataFrame
                df = pd.read_csv(file_path, delimiter=',')
                # unloading the column with the product name
                product_col = self._extract_column(df.columns, ['название', 'продукт', 'товар', 'наименование'])
                # unloading the column with the price of the product
                price_col = self._extract_column(df.columns, ['цена', 'розница'])
                # unloading the column with the weight of the product
                weight_col = self._extract_column(df.columns, ['вес', 'масса', 'фасовка'])
                if product_col and price_col and weight_col:  # Checking for all required columns
                    df = df[[product_col, price_col, weight_col]]  # We leave only the necessary columns in the DataFrame
                    df.columns = ['product_name', 'price', 'weight']  # Rename columns for convenience
                    df['file_name'] = file_name  # Adding a column with the file name
                    df['price_per_kg'] = df['price'] / df['weight']  # Adding a column with the price per kilogram
                    self.data = pd.concat([self.data, df], ignore_index=True)  #Combining the data with the previous ones

    def _extract_column(self, columns, possible_names):
        ''' Defining an auxiliary method for extracting the column name '''
        for name in possible_names:  # A loop to iterate through possible column names
            if name in columns:  # checking for a column in the DataFrame
                return name
        return None  # We return None if the column is not found

    def export_to_html(self, fname='output.html'):
        ''' Creates an HTML file with data about all products '''
        sorted_data = self.data.sort_values(by=['price_per_kg'])  # Sorting by cost per kilogram
        result = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Позиции продуктов</title>
        </head>
        <body>
            <table>
                <tr>
                    <th>Номер</th>
                    <th>Название</th>
                    <th>Цена</th>
                    <th>Фасовка</th>
                    <th>Файл</th>
                    <th>Цена за кг.</th>
                </tr>
        '''
        for i, row in sorted_data.iterrows():  # A loop for iterating over sorted data
            # Adding lines of HTML code with data to a table
            result += f''' 
                <tr>
                    <td>{i + 1}</td>
                    <td>{row['product_name']}</td>
                    <td>{row['price']}</td>
                    <td>{row['weight']}</td>
                    <td>{row['file_name']}</td>
                    <td>{row['price_per_kg']}</td>
                </tr>
            '''
        result += '''
            </table>
        </body>
        </html>
        '''
        # writing the code
        with open(fname, 'w') as file:
            file.write(result)

    def export_to_html_for_products(self, products, fname='output_for_products.html'):
        ''' Creates an HTML file with data about selected products '''
        if not products:
            print("Не указаны продукты для экспорта.")
            return
        sorted_data = self.data[self.data['product_name'].isin(products)].sort_values(by=['price_per_kg'])
        result = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Позиции продуктов</title>
        </head>
        <body>
            <table>
                <tr>
                    <th>Номер</th>
                    <th>Название</th>
                    <th>Цена</th>
                    <th>Фасовка</th>
                    <th>Файл</th>
                    <th>Цена за кг.</th>
                </tr>
        '''
        for i, row in sorted_data.iterrows():
            result += f'''
                <tr>
                    <td>{i + 1}</td>
                    <td>{row['product_name']}</td>
                    <td>{row['price']}</td>
                    <td>{row['weight']}</td>
                    <td>{row['file_name']}</td>
                    <td>{row['price_per_kg']}</td>
                </tr>
            '''
        result += '''
            </table>
        </body>
        </html>
        '''
        with open(fname, 'a') as file:  # We use the 'a' mode to add to the end of the file
            file.write(result)

    def find_text(self, text):
        ''' Search for products by text '''
        result = self.data[self.data['product_name'].str.contains(text, case=False)]
        sorted_result = result.sort_values(by=['price_per_kg'])  # Sorting by cost per kilogram
        return sorted_result


pm = PriceMachine()
pm.load_prices(folder_path='.')

while True:
    search_text = input("Введите фрагмент названия товара для поиска (для выхода введите 'exit'): ")
    if search_text.lower() == 'exit':
        print('Работа завершена.')
        break
    else:
        found_items = pm.find_text(search_text)
        if not found_items.empty:  # We check that the products have been found for the specified fragment
            print(found_items[['product_name', 'price', 'weight', 'file_name', 'price_per_kg']])
            pm.selected_products.extend(found_items['product_name'].tolist())  # Adding the selected products to the list
            add_more = input("Хотите добавить еще продукты в файл? (yes/no): ").lower()
            if add_more == 'no':
                export_choice = input("Хотите выгрузить результаты в HTML? (yes/no): ").lower()
                if export_choice == 'yes':
                    pm.export_to_html_for_products(pm.selected_products)
                    print("Результаты успешно выгружены в HTML.")
                break
        else:
            print('Товар не найден.')

# Exporting all products to HTML
pm.export_to_html()
